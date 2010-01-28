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

from plone.registry.interfaces import IRegistry

from zope.interface import implements, implementer
from zope.component import adapts, adapter, queryUtility

from zope.annotation.interfaces import IAnnotations, IAnnotatable

from zope.event import notify

from Acquisition import aq_base, aq_inner, aq_parent
from Acquisition import Explicit

from OFS.Traversable import Traversable

from OFS.event import ObjectWillBeAddedEvent
from OFS.event import ObjectWillBeRemovedEvent

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish

from Products.CMFPlone.interfaces import IPloneSiteRoot, INonStructuralFolder

from zope.container.contained import ContainerModifiedEvent

try:
    # Plone 4
    from zope.lifecycleevent import ObjectAddedEvent
    from zope.lifecycleevent import ObjectRemovedEvent
except:
    # Plone 3.x
    from zope.app.container.contained import ObjectAddedEvent
    from zope.app.container.contained import ObjectRemovedEvent

from BTrees.OIBTree import OIBTree

try:
    # These exist in new versions, but not in the one that comes with Zope 2.10.
    from BTrees.LOBTree import LOBTree
    from BTrees.LLBTree import LLSet
except ImportError:
    from BTrees.OOBTree import OOBTree as LOBTree
    from BTrees.OOBTree import OOSet as LLSet

from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IReplies
from plone.app.discussion.comment import Comment

ANNOTATION_KEY = 'plone.app.discussion:conversation'

class Conversation(Traversable, Persistent, Explicit):
    """A conversation is a container for all comments on a content object.

    It manages internal data structures for comment threading and efficient
    comment lookup.
    """

    implements(IConversation)

    __allow_access_to_unprotected_subobjects__ = True

    def __init__(self, id="++conversation++default"):
        self.id = id

        # username -> count of comments; key is removed when count reaches 0
        self._commentators = OIBTree()

        # id -> comment - find comment by id
        self._comments = LOBTree()

        # id -> LLSet (children) - find all children for a given comment.
        # 0 signifies root.
        self._children = LOBTree()

    def getId(self):
        """Get the id of the conversation. This is used to construct a
        URL.
        """
        return self.id

    def enabled(self):
        # Returns True if discussion is enabled on the conversation

        # Fetch discussion registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)

        # Check if discussion is allowed globally
        if not settings.globally_enabled:
            return False

        parent = aq_inner(self.__parent__)

        # Always return False if object is a folder
        if (IFolderish.providedBy(parent) and
            not INonStructuralFolder.providedBy(parent)):
            return False

        def traverse_parents(obj):
            # Run through the aq_chain of obj and check if discussion is
            # enabled in a parent folder.
            for obj in self.aq_chain:
                if not IPloneSiteRoot.providedBy(obj):
                    if (IFolderish.providedBy(obj) and
                        not INonStructuralFolder.providedBy(obj)):
                        flag = getattr(obj, 'allow_discussion', None)
                        if flag is not None:
                            return flag
            return None

        obj = aq_parent(self)

        # If discussion is disabled for the object, bail out
        obj_flag = getattr(obj, 'allow_discussion', None)
        if obj_flag is False:
            return False

        # Check if traversal returned a folder with discussion_allowed set
        # to True or False.
        folder_allow_discussion = traverse_parents(obj)

        if folder_allow_discussion is True:
            if not getattr(self, 'allow_discussion', None):
                return True
        elif folder_allow_discussion is False:
            if obj_flag:
                return True

        # Check if discussion is allowed on the content type
        portal_types = getToolByName(self, 'portal_types')
        document_fti = getattr(portal_types, obj.portal_type)
        if not document_fti.getProperty('allow_discussion'):
            # If discussion is not allowed on the content type,
            # check if 'allow discussion' is overridden on the content object.
            if not obj_flag:
                return False

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
        return self._commentators

    def objectIds(self):
        return self._comments.keys()

    def getComments(self, start=0, size=None):
        """Get unthreaded comments
        """
        count = 0l
        for comment in self._comments.values(min=start):
            yield comment

            count += 1
            if size and count > size:
                return

    def getThreads(self, start=0, size=None, root=0, depth=None):
        """Get threaded comments
        """

        def recurse(comment_id, d=0):
            # Yield the current comment before we look for its children
            yield {'id': comment_id, 'comment': self[comment_id], 'depth': d}

            # Recurse if there are children and we are not out of our depth
            if depth is None or d + 1 < depth:
                children = self._children.get(comment_id, None)
                if children is not None:
                    for child_id in children:
                        for value in recurse(child_id, d+1):
                            yield value

        # Find top level threads
        comments = self._children.get(root, None)
        if comments is not None:
            count = 0l
            for comment_id in comments.keys(min=start):

                # Abort if we have found all the threads we want
                count += 1
                if size and count > size:
                    return

                # Let the closure recurse
                for value in recurse(comment_id):
                    yield value

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

        comment.__parent__ = self

        # Record unique users who've commented (for logged in users only)
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

        return id

    # Dict API

    def __len__(self):
        return len(self._comments)

    def __contains__(self, key):
        return long(key) in self._comments

    def __getitem__(self, key):
        """Get an item by its long key
        """
        return self._comments[long(key)].__of__(self)

    def __delitem__(self, key, suppress_container_modified=False):
        """Delete an item by its long key
        """

        key = long(key)

        comment = self[key].__of__(self)
        commentator = comment.author_username

        notify(ObjectWillBeRemovedEvent(comment, self, key))

        # Remove all children
        for child_id in self._children.get(key, []):
            # avoid sending ContainerModifiedEvent multiple times
            self.__delitem__(child_id, suppress_container_modified=True)

            # XXX: During the events sent from the recursive deletion, the
            # _children data structure may be in an inconsistent state. We may
            # need to delay sending the events until it is fixed up.

        # Remove the comment from _comments
        self._comments.pop(key)

        # Remove this comment as a child of its parent
        if not suppress_container_modified:
            parent = comment.in_reply_to
            if parent is not None:
                parent_children = self._children.get(parent, None)
                if parent_children is not None and key in parent_children:
                    parent_children.remove(key)

        # Remove commentators
        if commentator and commentator in self._commentators:
            if self._commentators[commentator] <= 1:
                del self._commentators[commentator]
            else:
                self._commentators[commentator] -= 1

        notify(ObjectRemovedEvent(comment, self, key))

        if not suppress_container_modified:
            notify(ContainerModifiedEvent(self))

    def __iter__(self):
        return iter(self._comments)

    def get(self, key, default=None):
        comment = self._comments.get(long(key), default)
        if comment is default:
            return default
        return comment.__of__(self)

    def keys(self):
        return self._comments.keys()

    def items(self):
        return [(i[0], i[1].__of__(self),) for i in self._comments.items()]

    def values(self):
        return [v.__of__(self) for v in self._comments.values()]

    def iterkeys(self):
        return self._comments.iterkeys()

    def itervalues(self):
        for v in self._comments.itervalues():
            yield v.__of__(self)

    def iteritems(self):
        for k, v in self._comments.iteritems():
            yield (k, v.__of__(self),)


@implementer(IConversation)
@adapter(IAnnotatable)
def conversationAdapterFactory(content):
    """Adapter factory to fetch the default conversation from annotations.
    Will create the conversation if it does not exist.
    """
    annotions = IAnnotations(content)
    if not ANNOTATION_KEY in annotions:
        conversation = Conversation()
        conversation.__parent__ = aq_base(content)
        annotions[ANNOTATION_KEY] = conversation
    else:
        conversation = annotions[ANNOTATION_KEY]
    return conversation.__of__(content)


try:
    from Products.LinguaPlone.interfaces import ITranslatable
except ImportError:
    pass
else:
    @implementer(IConversation)
    @adapter(IAnnotatable)
    def conversationCanonicalAdapterFactory(content):
        """Adapter factory to fetch the default conversation from annotations.
        Will create the conversation if it does not exist.

        This adapter will fetch and store all comments on the canonical object,
        so that comments will be shared across all translations.
        """
        if ITranslatable.providedBy(content):
            content = content.getCanonical()
        return conversationAdapterFactory(content)


class ConversationReplies(object):
    """An IReplies adapter for conversations.

    This makes it easy to work with top-level comments.
    """

    implements(IReplies)
    adapts(Conversation) # relies on implementation details

    def __init__(self, context):
        self.conversation = context
        self.comment_id = 0l

    def addComment(self, comment):
        comment.in_reply_to = None
        return self.conversation.addComment(comment)

    # Dict API

    def __len__(self):
        return len(self.children)

    def __contains__(self, key):
        return long(key) in self.children

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

    @property
    def children(self):
        # we need to look this up every time, because we may not have a
        # dict yet when the adapter is first created
        return self.conversation._children.get(self.comment_id, LLSet())

class CommentReplies(ConversationReplies):
    """An IReplies adapter for comments.

    This makes it easy to work with replies to specific comments.
    """

    implements(IReplies)

    # depends on implementation details of conversation
    # most likely, anyone writing a different type of Conversation will also
    # have a different type of Comment

    adapts(Comment)

    def __init__(self, context):
        self.comment = context
        self.conversation = aq_parent(self.comment)

        if (self.conversation is None or
            not hasattr(self.conversation, '_children')):
            raise TypeError("This adapter doesn't know what to do with the "
                            "parent conversation")

        self.comment_id = self.comment.comment_id

    def addComment(self, comment):
        comment.in_reply_to = self.comment_id
        return self.conversation.addComment(comment)

    # Dict API is inherited, written in terms of self.conversation and self.children
