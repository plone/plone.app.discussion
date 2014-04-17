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

        # Add comment on session to easily define content-rules dynamic strings
        sdm = getattr(context, 'session_data_manager', None)
        session = sdm.getSessionData(create=True) if sdm else None

        if session:
            sessionComment = dict(
                (field, getattr(comment, field, None)) for field in IComment
                if not field.startswith('_')
            )
            session.set('comment', sessionComment)

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
