""" Custom discussion events
"""
from zope.interface import implements
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IDiscussionEvent
from plone.app.discussion.interfaces import ICommentAddedEvent
from plone.app.discussion.interfaces import ICommentRemovedEvent
from plone.app.discussion.interfaces import IReplyAddedEvent
from plone.app.discussion.interfaces import IReplyRemovedEvent

class DiscussionEvent(object):
    """ Custom event
    """
    implements(IDiscussionEvent)

    def __init__(self, context, comment, **kwargs):
        self.object = context
        self.comment = comment
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Add event to the request to be able to access comment attributes
        # in content-rules dynamic strings
        request = context.REQUEST
        request.set('event', self)

class CommentAddedEvent(DiscussionEvent):
    """ Event to be triggered when a Comment is added
    """
    implements(ICommentAddedEvent)

class CommentRemovedEvent(DiscussionEvent):
    """ Event to be triggered when a Comment is removed
    """
    implements(ICommentRemovedEvent)

class ReplyAddedEvent(DiscussionEvent):
    """ Event to be triggered when a Comment reply is added
    """
    implements(IReplyAddedEvent)

class ReplyRemovedEvent(DiscussionEvent):
    """ Event to be triggered when a Comment reply is removed
    """
    implements(IReplyRemovedEvent)
