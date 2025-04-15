"""Custom discussion events"""

from plone.app.discussion.interfaces import ICommentAddedEvent
from plone.app.discussion.interfaces import ICommentDeletedEvent
from plone.app.discussion.interfaces import ICommentModifiedEvent
from plone.app.discussion.interfaces import ICommentPublishedEvent
from plone.app.discussion.interfaces import ICommentRemovedEvent
from plone.app.discussion.interfaces import ICommentTransitionEvent
from plone.app.discussion.interfaces import IDiscussionEvent
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IReplyAddedEvent
from plone.app.discussion.interfaces import IReplyModifiedEvent
from plone.app.discussion.interfaces import IReplyRemovedEvent
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
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


def auto_approve_comments(obj, event):
    """Auto-approve comments for users with 'Review comments' permission."""
    # Check if comment moderation is enabled
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)

    if not settings.moderation_enabled:
        return

    # Get the user who created the comment
    mtool = getToolByName(obj, "portal_membership")
    member = mtool.getAuthenticatedMember()

    # Check if user has 'Review comments' permission
    if member.has_permission("Review comments", obj):
        # Auto-approve the comment
        workflow_tool = getToolByName(obj, "portal_workflow")
        current_state = workflow_tool.getInfoFor(obj, "review_state")

        if current_state == "pending":
            workflow_tool.doActionFor(obj, "publish")
