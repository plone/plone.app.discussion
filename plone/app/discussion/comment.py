"""The default comment class and factory.
"""
from datetime import datetime
from zope.interface import implements
from zope.component.factory import Factory

from Acquisition import Explicit
from OFS.Traversable import Traversable
from AccessControl.Role import RoleManager
from AccessControl.Owned import Owned

from plone.app.discussion.interfaces import IComment

class Comment(Explicit, Traversable, RoleManager, Owned):
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
    
    def __init__(self, conversation=None, **kw):
        self.comment_id = None # will be set by IConversation.addComment()

        self.__parent__ = conversation
        self.creation_date = self.modification_date = datetime.now()
        
        for k, v in kw.items():
            setattr(self, k, v)

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

CommentFactory = Factory(Comment)