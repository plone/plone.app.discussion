"""The default comment class and factory.
"""
from DateTime import DateTime
from zope.interface import implements
from zope.component.factory import Factory

from Acquisition import Explicit
from OFS.Traversable import Traversable
from AccessControl.Role import RoleManager
from AccessControl.Owned import Owned

from plone.app.discussion.interfaces import IComment

from Products.CMFCore.DynamicType import DynamicType
from Products.CMFCore.utils import getToolByName

class Comment(DynamicType, Traversable, RoleManager, Owned, Explicit):
    """A comment.

    This object attempts to be as lightweight as possible. We implement a
    number of standard methods instead of subclassing, to have total control
    over what goes into the object.
    """

    implements(IComment)

    meta_type = portal_type = 'Discussion Item'

    __parent__ = None

    comment_id = None # long
    in_reply_to = None # long

    title = u""

    mime_type = "text/plain"
    text = u""

    creator = None
    creation_date = None
    modification_date = None

    author_username = None

    author_name = None
    author_email = None

    # Note: we want to use zope.component.createObject() to instantiate
    # comments as far as possible. comment_id and __parent__ are set via
    # IConversation.addComment().

    def __init__(self):
        self.creation_date = self.modification_date = DateTime()

    @property
    def __name__(self):
        return self.comment_id and unicode(self.comment_id) or None

    @property
    def id(self):
        return self.comment_id and str(self.comment_id) or None

    def getId(self):
        """The id of the comment, as a string
        """
        return self.id

    def Title(self):
        """The title of the comment
        """
        return self.title

    def Creator(self):
        """The name of the person who wrote the comment
        """
        return self.creator

    # CMF's event handlers assume any IDynamicType has these :(

    def opaqueItems(self):
        return []

    def opaqueIds(self):
        return []

    def opaqueValues(self):
        return []

CommentFactory = Factory(Comment)

def notify_workflow(obj, event):
    """Tell the workflow tool when a comment is added
    """
    tool = getToolByName(obj, 'portal_workflow', None)
    if tool is not None:
        tool.notifyCreated(obj)