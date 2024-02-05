""" Custom discussion events
"""

from plone.app.discussion.interfaces import ICommentAddedEvent
from plone.app.discussion.interfaces import ICommentDeletedEvent
from plone.app.discussion.interfaces import ICommentModifiedEvent
from plone.app.discussion.interfaces import ICommentPublishedEvent
from plone.app.discussion.interfaces import ICommentRemovedEvent
from plone.app.discussion.interfaces import ICommentTransitionEvent
from plone.app.discussion.interfaces import IDiscussionEvent
from plone.app.discussion.interfaces import IReplyAddedEvent
from plone.app.discussion.interfaces import IReplyModifiedEvent
from plone.app.discussion.interfaces import IReplyRemovedEvent
from zope.interface import implementer


@implementer(IDiscussionEvent)
class DiscussionEvent:
    """Custom event"""

    def __init__(self, context, comment, **kwargs):
        self.object = context
        self.comment = comment
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Add event to the request to be able to access comment attributes
        # in content-rules dynamic strings
        request = context.REQUEST
        request.set("event", self)


@implementer(ICommentAddedEvent)
class CommentAddedEvent(DiscussionEvent):
    """Event to be triggered when a Comment is added"""


@implementer(ICommentModifiedEvent)
class CommentModifiedEvent(DiscussionEvent):
    """Event to be triggered when a Comment is modified"""


@implementer(ICommentRemovedEvent)
class CommentRemovedEvent(DiscussionEvent):
    """Event to be triggered when a Comment is removed"""


@implementer(IReplyAddedEvent)
class ReplyAddedEvent(DiscussionEvent):
    """Event to be triggered when a Comment reply is added"""


@implementer(IReplyModifiedEvent)
class ReplyModifiedEvent(DiscussionEvent):
    """Event to be triggered when a Comment reply is modified"""


@implementer(IReplyRemovedEvent)
class ReplyRemovedEvent(DiscussionEvent):
    """Event to be triggered when a Comment reply is removed"""


@implementer(ICommentDeletedEvent)
class CommentDeletedEvent(DiscussionEvent):
    """Event to be triggered when a Comment is deleted"""


@implementer(ICommentPublishedEvent)
class CommentPublishedEvent(DiscussionEvent):
    """Event to be triggered when a Comment is publicated"""


@implementer(ICommentTransitionEvent)
class CommentTransitionEvent(DiscussionEvent):
    """Event to be triggered when a Comments review_state changed."""
