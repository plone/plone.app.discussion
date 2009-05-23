"""Implement the ++comments++ traversal namespace. This should return the
IDiscussion container for the context, from which traversal will continue
into an actual comment object.
"""

from zope.interface import Interface, implements
from zope.component import adapts

from zope.traversing.interfaces import ITraversable, TraversalError
from zope.publisher.interfaces.browser import IBrowserRequest

from plone.app.discussion.interfaces import IConversation

class ConversationNamespace(object):
    """Allow traversal into a conversation
    """
    implements(ITraversable)
    adapts(Interface, IBrowserRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        
        conversation = IConversation(self.context, None)
        if conversation is None:
            raise TraversalError('++comment++')
        
        return conversation.__of__(self.context)
