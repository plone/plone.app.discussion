"""The conversation and replies adapters

The conversation is responsible for storing all comments. It provides a
dict-like API for accessing comments, where keys are integers and values
are IComment objects. It also provides features for finding comments quickly.

The two IReplies adapters - one for the IConversation and one for IComment -
manipulate the same data structures, but provide an API for finding and
manipulating the comments directly in reply to a particular comment or at the
top level of the conversation.
"""

from persistent import Persistent

from zope.interface import implements, implementer
from zope.component import adapts, adapter
from zope.annotation.interfaces import IAnnotations

from zope.event import notify
from zope.app.container.interfaces import IObjectAddedEvent
from OFS.event import ObjectWillBeAddedEvent
from OFS.event import ObjectWillBeRemovedEvent
from zope.app.container.contained import ContainerModifiedEvent
from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import ObjectRemovedEvent

from zope.annotation.interfaces import IAnnotatable

from BTrees.OIBTree import OIBTree
from BTrees.IOBTree import IOBTree
from BTrees.IIBTree import IIBTree, IISet
try:
    # These exist in new versions, but not in the one that comes with Zope 2.10.
    from BTrees.LOBTree import LOBTree
    from BTrees.LLBTree import LLSet
except ImportError:
    from BTrees.OOBTree import OOBTree as LOBTree
    from BTrees.OOBTree import OOSet as LLSet


from Acquisition import Explicit
from plone.app.discussion.interfaces import IConversation, IComment, IReplies

ANNO_KEY = 'plone.app.discussion:conversation'

class Conversation(Persistent, Explicit):
    """A conversation is a container for all comments on a content object.
    
    It manages internal data structures for comment threading and efficient
    comment lookup.
    """
    
    implements(IConversation)
    
    def __init__(self, id="++comments++"):
        self.id = id
        
        # username -> count of comments; key is removed when count reaches 0
        self._commentators = OIBTree()
        self._last_comment_date = None
        
        # id -> comment - find comment by id
        self._comments = LOBTree()  
        
        # id -> IISet (children) - find all children for a given comment. 0 signifies root.
        self._children = LOBTree()
        
    def getId(self):
        """
        """
        return self.id
    
    @property
    def enabled(self):
        # TODO
        return True
    
    @property
    def total_comments(self):
        # TODO
        return len(self._comments)
    
    @property
    def last_comment_date(self):
        return self._last_comment_date
    
    @property
    def commentators(self):
        # TODO:
        return set()
    
    def getComments(self, start=0, size=None):
        return self._comments.values()
    
    def getThreads(self, start=0, size=None, root=None, depth=None):
        # TODO:
        return self._comments.values()
    
    def addComment(self, comment):
        id = comment.comment_id
        if id in self._comments:
            id = max(self._comments.keys()) + 1
        notify(ObjectWillBeAddedEvent(comment, self, id))
        self._comments[id] = comment
        comment.comment_id = id
        
        commentator = comment.creator
        if not commentator in self._commentators:
            self._commentators[commentator] = 0
        self._commentators[commentator] += 1
        
        self._last_comment_date = comment.creation_date
        
        reply_to = comment.in_reply_to
        if not reply_to in self._children:
            self._children[reply_to] = LLSet()
        self._children[reply_to].insert(id)
        # Notify that the object is added. The object must here be
        # acquisition wrapped or the indexing will fail.
        notify(ObjectAddedEvent(comment.__of__(self), self, id))
        notify(ContainerModifiedEvent(self))
        
    # Dict API
    
    def __getitem__(self, key):
        return self._comments[key]
    
    def __setitem__(self, key, value):
        # XXX Check that it implements the commenting interface
        if value.comment_id in self._comments:
            raise ValueError("Can not replace an existing comment")
        # Note that we ignore the key completely:
        self.addComment(comment)
            
    def __delitem__(self, key):
        # TODO unindex everything
        return self._comments.remove(key)
    
    def keys(self):
        return self._comments.keys()
    
    def getPhysicalPath(self):
        return self.aq_parent.getPhysicalPath() + (self.id,)
    
    # TODO: Update internal data structures when items added or removed

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
    # Probably this needs an acquisition wrapper
    return conversation

class ConversationReplies(object):
    """An IReplies adapter for conversations.
    
    This makes it easy to work with top-level comments.
    """
    
    implements(IReplies)
    adapts(Conversation)
    
    def __init__(self, context):
        self.conversation = context
        self.root = 0
    
    # TODO: dict interface - generalise to work with any starting point, so
    # that the subclassing below works

class CommentReplies(ConversationReplies):
    """An IReplies adapter for comments.
    
    This makes it easy to work with replies to specific comments.
    """
    
    implements(IReplies)
    adapts(IComment)
    
    def __init__(self, context):
        self.conversation = context.__parent__
        self.root = context.comment_id
