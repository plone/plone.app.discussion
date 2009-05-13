"""The default comment class and factory.
"""

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
    __name__ = None

    title = u""
    
    mime_type = "text/plain"
    text = u""
    
    creator = None
    creation_date = None
    modification_date = None
    
    author_username = None
    
    author_name = None
    author_email = None
    
    def __init__(self, id=None, conversation=None, **kw):
        self.__name__ = unicode(id)
        self.__parent__ = conversation
        
        for k, v in kw:
            setattr(self, k, v)
    
    # convenience functions
    
    @property
    def id(self):
        return str(self.__name__)
    
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