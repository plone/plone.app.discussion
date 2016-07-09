# -*- coding: utf-8 -*-
"""The conversation and replies adapters

The conversation is responsible for storing all comments. It provides a
dict-like API for accessing comments, where keys are integers and values
are IComment objects. It also provides features for finding comments quickly.

The two IReplies adapters - one for the IConversation and one for IComment -
manipulate the same data structures, but provide an API for finding and
manipulating the comments directly in reply to a particular comment or at the
top level of the conversation.
"""
from AccessControl.SpecialUsers import nobody as user_nobody
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import Explicit
from BTrees.LLBTree import LLSet
from BTrees.LOBTree import LOBTree
from BTrees.OIBTree import OIBTree
from OFS.event import ObjectWillBeAddedEvent
from OFS.event import ObjectWillBeRemovedEvent
from OFS.Traversable import Traversable
from persistent import Persistent
from plone.app.discussion.comment import Comment
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IReplies
from Products.CMFPlone import DISCUSSION_ANNOTATION_KEY as ANNOTATION_KEY
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import adapts
from zope.container.contained import ContainerModifiedEvent
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectRemovedEvent

import time


@implementer(IConversation, IHideFromBreadcrumbs)
class Conversation(Traversable, Persistent, Explicit):
    """A conversation is a container for all comments on a content object.

    It manages internal data structures for comment threading and efficient
    comment lookup.
    """

    __allow_access_to_unprotected_subobjects__ = True

    def __init__(self, id='++conversation++default'):
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
        parent = aq_inner(self.__parent__)
        return parent.restrictedTraverse('@@conversation_view').enabled()

    def total_comments(self):
        public_comments = [
            x for x in self.values()
            if user_nobody.has_permission('View', x)
        ]
        return len(public_comments)

    @property
    def last_comment_date(self):
        # self._comments is an Instance of a btree. The keys
        # are always ordered
        comment_keys = self._comments.keys()
        for comment_key in reversed(comment_keys):
            comment = self._comments[comment_key]
            if user_nobody.has_permission('View', comment):
                return comment.creation_date
        return None

    @property
    def commentators(self):
        return self._commentators

    @property
    def public_commentators(self):
        retval = set()
        for comment in self._comments.values():
            if not user_nobody.has_permission('View', comment):
                continue
            retval.add(comment.author_username)
        return tuple(retval)

    def objectIds(self):
        return self._comments.keys()

    def getComments(self, start=0, size=None):
        """Get unthreaded comments
        """
        count = 0l
        for comment in self._comments.values(min=start):
            # Yield the acquisition wrapped comment
            yield self[comment.id]

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
                        for value in recurse(child_id, d + 1):
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

        comment.__parent__ = aq_base(self)

        # Record unique users who've commented (for logged in users only)
        commentator = comment.author_username
        if commentator:
            if commentator not in self._commentators:
                self._commentators[commentator] = 0
            self._commentators[commentator] += 1

        reply_to = comment.in_reply_to
        if not reply_to:
            # top level comments are in reply to the faux id 0
            comment.in_reply_to = reply_to = 0

        if reply_to not in self._children:
            self._children[reply_to] = LLSet()
        self._children[reply_to].insert(id)

        # Add the annotation if not already done
        annotions = IAnnotations(self.__parent__)
        if ANNOTATION_KEY not in annotions:
            annotions[ANNOTATION_KEY] = aq_base(self)

        # Notify that the object is added. The object must here be
        # acquisition wrapped or the indexing will fail.
        notify(ObjectCreatedEvent(comment))
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
        try:
            comment_id = long(key)
        except ValueError:
            return
        return self._comments[comment_id].__of__(self)

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

    def allowedContentTypes(self):
        return []


@implementer(IConversation)
@adapter(IAnnotatable)
def conversationAdapterFactory(content):
    """
    Adapter factory to fetch the default conversation from annotations.
    """
    annotations = IAnnotations(content)
    if ANNOTATION_KEY not in annotations:
        conversation = Conversation()
        conversation.__parent__ = aq_base(content)
    else:
        conversation = annotations[ANNOTATION_KEY]
    return conversation.__of__(content)


try:
    from Products.LinguaPlone.interfaces import ITranslatable
except ImportError:
    pass
else:
    @implementer(IConversation)  # pragma: no cover
    @adapter(IAnnotatable)  # pragma: no cover
    def conversationCanonicalAdapterFactory(content):  # pragma: no cover
        """Adapter factory to fetch the default conversation from annotations.
        Will create the conversation if it does not exist.

        This adapter will fetch and store all comments on the canonical object,
        so that comments will be shared across all translations.
        """
        if ITranslatable.providedBy(content):
            canonical = content.getCanonical()
            if canonical is not None:
                return conversationAdapterFactory(canonical)
        return conversationAdapterFactory(content)


@implementer(IReplies)
class ConversationReplies(object):
    """An IReplies adapter for conversations.

    This makes it easy to work with top-level comments.
    """
    adapts(Conversation)  # relies on implementation details

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


@implementer(IReplies)
class CommentReplies(ConversationReplies):
    """An IReplies adapter for comments.

    This makes it easy to work with replies to specific comments.
    """

    # depends on implementation details of conversation
    # most likely, anyone writing a different type of Conversation will also
    # have a different type of Comment

    adapts(Comment)

    def __init__(self, context):
        self.comment = context
        self.conversation = aq_parent(self.comment)
        conversation_has_no_children = not hasattr(
            self.conversation,
            '_children'
        )
        if self.conversation is None or conversation_has_no_children:
            raise TypeError("This adapter doesn't know what to do with the "
                            'parent conversation')

        self.comment_id = self.comment.comment_id

    def addComment(self, comment):
        comment.in_reply_to = self.comment_id
        return self.conversation.addComment(comment)

    # Dict API is inherited, written in terms of self.conversation and
    # self.children
