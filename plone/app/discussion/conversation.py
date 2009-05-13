"""The conversation and replies adapters

The conversation is responsible for storing all comments. It provides a
dict-like API for accessing comments, where keys are integers and values
are IComment objects. It also provides features for finding comments quickly.

The two IReplies adapters - one for the IConversation and one for IComment -
manipulate the same data structures, but provide an API for finding and
manipulating the comments directly in reply to a particular comment or at the
top level of the conversation.
"""

from zope.interface import implements
from zope.component import adapts

from BTrees.OIBTree import OIBTree
from BTrees.IOBTree import IOBTree
from BTrees.IIBTree import IIBTree, IISet

from Acquisition import Explicit

from plone.app.discussion.interfaces import IConversation, IComment, IReplies

class Conversation(Explicit):
    """A conversation is a container for all comments on a content object.
    """
    
    implements(IConversation)
    
    def __init__(self, id="++comments++"):
        self.id = id
        
        # username -> count of comments; key is removed when count reaches 0
        self._commentators = OIBTree()
        self._last_comment_date = None
        
        # id -> comment - find comment by id
        self._comments = IOBTree()  
        
        # # id -> IISet (children) - find all children for a given comment. 0 signifies root.
        self._children = IOBTree()
        
        # id -> id (parent) - find the parent for a given comment. 0 signifies root
        self._parents  = IIBTree()
    
    def getId(self):
        """
        """
        return self.id
    
    @property
    def enabled(self):
        # TODO
        return True
    
    @property
    def total_comments(self):
        # TODO
        return 0
    
    @property
    def last_comment_date(self):
        # TODO
        return None
    
    @property
    def commentators(self):
        # TODO:
        return set()
    
    def getComments(start=0, size=None):
        # TODO
        pass
    
    def getThreads(start=0, size=None, root=None, depth=None):
        # TODO
        pass
    
    # Dict API
    
    # TODO: Update internal data structures when items added or removed
    
class ConversationReplies(object):
    """
    """
    
    implements(IReplies)
    adapts(Conversation)

class CommentReplies(object):
    """
    """
    
    implements(IReplies)
    adapts(IComment)