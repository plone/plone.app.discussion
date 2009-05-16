import time
from zope import interface
from zope.component import getUtility

from BTrees.OOBTree import OOBTree, OOSet, intersection

from interfaces import ICommentingTool
# The commenting tool, which is a local utility

class CommentingTool(object):
    interface.implements(ICommentingTool)
    
    def __init__(self):
        self._id2uid = OOBTree() # The comment ID to object UID
        self._id2text = OOBTree() # The text for a comment
        self._wfstate2id = OOBTree() # To search on wf states
        self._creator2id = OOBTree() # To search/order on creator ids
                
    def index(self, comment):
        # Store the object in the store:
        id = comment.comment_id
        self._id2uid[id] = comment.__parent__._parent_uid
        self._id2text[id] = comment.text

        # TODO
        ## Index on workflow state
        #wfstate = comment.getWorkflowState()
        #if not wfstate in self._wfstate2id:
            #self._wfstate2id[wfstate] = OOSet()
        #self._wfstate2id[wfstate].insert(id)

        # Index on creator
        creator = comment.creator
        if not creator in self._creator2id:
            self._creator2id[creator] = OOSet()
        self._creator2id[creator].insert(id)
            
    def search(self, creator=None):
        if creator is not None:
            # Get all replies for a certain object
            ids = self._creator2ids.get(creator, None)
            if ids is None:
                raise StopIteration
        else:
            ids = self._id2uid.keys()
                        
        for id in ids:
            yield {'id': id,
                   'text': self._id2text[id]
                   # TODO: More data + maybe brains or something?
                   }

def object_added_handler(obj, event):
    tool = getUtility(ICommentingTool)
    tool.index(obj)
    
def object_removed_handler(obj, event):
    tool = getUtility(ICommentingTool)
    tool.unindex(obj)
