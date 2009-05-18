"""The conversation and replies adapters

The conversation is responsible for storing all comments. It provides a
dict-like API for accessing comments, where keys are integers and values
are IComment objects. It also provides features for finding comments quickly.

The two IReplies adapters - one for the IConversation and one for IComment -
manipulate the same data structures, but provide an API for finding and
manipulating the comments directly in reply to a particular comment or at the
top level of the conversation.
"""

import time

from persistent import Persistent

from zope.interface import implements, implementer
from zope.component import adapts, adapter
from zope.annotation.interfaces import IAnnotations

from zope.event import notify

from Acquisition import Explicit
from OFS.Traversable import Traversable

from OFS.event import ObjectWillBeAddedEvent
from OFS.event import ObjectWillBeRemovedEvent

from zope.app.container.contained import ContainerModifiedEvent

from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import ObjectRemovedEvent

from zope.annotation.interfaces import IAnnotatable

from BTrees.OIBTree import OIBTree

try:
    # These exist in new versions, but not in the one that comes with Zope 2.10.
    from BTrees.LOBTree import LOBTree
    from BTrees.LLBTree import LLSet
except ImportError:
    from BTrees.OOBTree import OOBTree as LOBTree
    from BTrees.OOBTree import OOSet as LLSet

from plone.app.discussion.interfaces import IConversation, IComment, IReplies

from Acquisition import aq_base

ANNO_KEY = 'plone.app.discussion:conversation'

class Conversation(Traversable, Persistent, Explicit):
    """A conversation is a container for all comments on a content object.
    
    It manages internal data structures for comment threading and efficient
    comment lookup.
    """
    
    implements(IConversation)
    
    def __init__(self, id="++comments++"):
        self.id = id
        
        # username -> count of comments; key is removed when count reaches 0
        self._commentators = OIBTree()
        
        # id -> comment - find comment by id
        self._comments = LOBTree()  
        
        # id -> IISet (children) - find all children for a given comment. 0 signifies root.
        self._children = LOBTree()
        
    def getId(self):
        """Get the id of 
        """
        return self.id
    
    @property
    def enabled(self):
        # TODO - check __parent__'s settings + global settings
        return True
    
    @property
    def total_comments(self):
        return len(self._comments)
    
    @property
    def last_comment_date(self):
        try:
            return self._comments[self._comments.maxKey()].creation_date
        except (ValueError, KeyError, AttributeError,):
            return None
    
    @property
    def commentators(self):
        return self._commentators.keys()
    
    def getComments(self, start=0, size=None):
        """Get unthreaded comments
        """
        # TODO - batching
        return self._comments.values()
    
    def getThreads(self, start=0, size=None, root=None, depth=None):
        """Get threaded comments
        """
        # TODO - build threads
        return self._comments.values()
    
    def addComment(self, comment):
        """Add a new comment. The parent id should have been set already. The
        comment id may be modified to find a free key. The id used will be
        returned.
        """
        
        # Make sure we don't have a wrapped object
        
        comment = aq_base(comment)
        
        id = long(time.time() * 1e6)
        while id in self._comments:
            id += 1
        
        comment.comment_id = id
        notify(ObjectWillBeAddedEvent(comment, self, id))
        self._comments[id] = comment
        
        # for logged in users only
        commentator = comment.author_username
        if commentator:
            if not commentator in self._commentators:
                self._commentators[commentator] = 0
            self._commentators[commentator] += 1
        
        reply_to = comment.in_reply_to
        if not reply_to:
            # top level comments are in reply to the faux id 0
            comment.in_reply_to = reply_to = 0
        
        if not reply_to in self._children:
            self._children[reply_to] = LLSet()
        self._children[reply_to].insert(id)
        
        # Notify that the object is added. The object must here be
        # acquisition wrapped or the indexing will fail.
        notify(ObjectAddedEvent(comment.__of__(self), self, id))
        notify(ContainerModifiedEvent(self))
        
    # Dict API
    
    def __len__(self):
        return len(self._comments)
    
    def __contains__(self, key):
        return long(key) in self._comments
    
    # TODO: Should __getitem__, get, __iter__, values(), items() and iter* return aq-wrapped comments?
    
    def __getitem__(self, key):
        """Get an item by its long key
        """
        return self._comments[long(key)]
    
    def __delitem__(self, key):
        """Delete an item by its long key
        """
        
        key = long(key)
        
        comment = self[key]
        commentator = comment.author_username
        
        notify(ObjectWillBeRemovedEvent(comment, self, key))
        self._comments.remove(key)
        notify(ObjectRemovedEvent(comment, self, key))
        
        if commentator and commentator in self._commentators:
            if self._commentators[commentator] <= 1:
                del self._commentators[commentator]
            else:
                self._commentators[commentator] -= 1
        
        notify(ContainerModifiedEvent(self))
    
    def __iter__(self):
        return iter(self._comments)
    
    def get(self, key, default=None):
        return self._comments.get(long(key), default)
    
    def keys(self):
        return self._comments.keys()
    
    def items(self):
        return self._comments.items()
    
    def values(self):
        return self._comments.values()
    
    def iterkeys(self):
        return self._comments.iterkeys()
    
    def itervalues(self):
        return self._comments.itervalues()
    
    def iteritems(self):
        return self._comments.iteritems()

@implementer(IConversation)
@adapter(IAnnotatable)
def conversationAdapterFactory(content):
    """Adapter factory to fetch a conversation from annotations
    """
    annotions = IAnnotations(content)
    if not ANNO_KEY in annotions:
        conversation = Conversation()
        conversation._parent_uid = content.UID()
        annotions[ANNO_KEY] = conversation
    conversation = annotions[ANNO_KEY]
    return conversation

class ConversationReplies(object):
    """An IReplies adapter for conversations.
    
    This makes it easy to work with top-level comments.
    """
    
    implements(IReplies)
    adapts(Conversation) # relies on implementation details
    
    def __init__(self, context):
        self.conversation = context
        self.children = self.conversation._children.get(0, LLSet())
    
    def addComment(self, comment):
        comment.in_reply_to = None
        return self.conversation.addComment(comment)
        
    # Dict API
    
    def __len__(self):
        return len(self.children)
    
    def __contains__(self, key):
        return long(key) in self.children
    
    # TODO: Should __getitem__, get, __iter__, values(), items() and iter* return aq-wrapped comments?
    
    def __getitem__(self, key):
        """Get an item by its long key
        """
        key = long(key)
        if key not in self.children:
            raise KeyError(key)
        return self.conversation[key]
    
    def __delitem__(self, key):
        """Delete an item by its long key
        """
        key = long(key)
        if key not in self.children:
            raise KeyError(key)
        del self.conversation[key]
    
    def __iter__(self):
        return iter(self.children)
    
    def get(self, key, default=None):
        key = long(key)
        if key not in self.children:
            return default
        return self.conversation.get(key)
    
    def keys(self):
        return self.children
    
    def items(self):
        return [(k, self.conversation[k]) for k in self.children]
    
    def values(self):
        return [self.conversation[k] for k in self.children]
    
    def iterkeys(self):
        return iter(self.children)
    
    def itervalues(self):
        for key in self.children:
            yield self.conversation[key]
    
    def iteritems(self):
        for key in self.children:
            yield (key, self.conversation[key],)

class CommentReplies(ConversationReplies):
    """An IReplies adapter for comments.
    
    This makes it easy to work with replies to specific comments.
    """
    
    implements(IReplies)
    adapts(IComment)
    
    def __init__(self, context):
        self.comment = context
        self.comment_id = context.comment_id
        self.children = self.conversation._children.get(0, LLSet())
    
    def addComment(self, comment):
        comment.in_reply_to = self.comment_id
        return self.conversation.addComment(comment)
    
    # Dict API is inherited
