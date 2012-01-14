"""Implement the ++comments++ traversal namespace. This should return the
IDiscussion container for the context, from which traversal will continue
into an actual comment object.
"""

from zope.interface import Interface, implements
from zope.component import adapts, queryAdapter

from zope.traversing.interfaces import ITraversable, TraversalError
from zope.publisher.interfaces.browser import IBrowserRequest

from plone.app.discussion.interfaces import IConversation


class ConversationNamespace(object):
    """Allow traversal into a conversation via a ++conversation++name
    namespace. The name is the name of an adapter from context to
    IConversation. The special name 'default' will be taken as the default
    (unnamed) adapter. This is to work around a bug in OFS.Traversable which
    does not allow traversal to namespaces with an empty string name.
    """

    implements(ITraversable)
    adapts(Interface, IBrowserRequest)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):

        if name == "default":
            name = u""

        conversation = queryAdapter(self.context, IConversation, name=name)
        if conversation is None:
            raise TraversalError(name)  # pragma: no cover

        return conversation
