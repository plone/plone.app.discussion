"""Discussion items and replies
"""

from zope.interface import implements, alsoProvides

from BTrees.OOBTree import OOBTree

from Acquisition import Explicit
from OFS.Traversable import Traversable
from AccessControl.Role import RoleManager
from AccessControl.Owned import Owned

from plone.app.discussion.interfaces import IReplies, IComment

def Replies():
    """Create a new replies object. Acts like a constructor, but actually
    returns a BTree marked with an interface. We do this because subclassing
    an OOBTree does not work properly.
    """
    
    replies = OOBTree()
    alsoProvides(replies, IReplies)
    return replies

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
    ancestor = None

    title = u""
    mime_type = "text/plain"
    
    text = u""
    
    creator = None
    creation_date = None
    modification_date = None
    
    author_username = None
    
    author_name = None
    author_email = None
    
    replies = None
    
    def __init__(self, id, ancestor, parent, **kw):
        self.__name__ = id
        self.__parent__ = parent
        self.ancestor = ancestor
        
        for k, v in kw:
            setattr(self, k, v)
        
        replies = Replies()
    
    # convenience functions
    
    @property
    def id(self):
        return self.__name__
    
    def getId(self):
        return self.__name__
