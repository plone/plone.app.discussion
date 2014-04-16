""" Content rules handlers
"""
from Acquisition import aq_parent
from plone.app.contentrules.handlers import execute
from plone.stringinterp import adapters

def execute_comment(event):
    """ Execute comment content rules
    """
    execute(event.object, event)

#
# String interp for comment's content rules
#
class Mixin(object):
    """ Override context
    """
    @property
    def context(self):
        """ Getter
        """
        conversation = aq_parent(self._context)
        return aq_parent(conversation)

    @context.setter
    def context(self, value):
        """ Setter
        """
        self._context = value


class CommentUrlSubstitution(adapters.UrlSubstitution, Mixin):
    """ Override context to be used for URL substitution
    """

class CommentParentUrlSubstitution(adapters.ParentUrlSubstitution, Mixin):
    """ Override context to be used for Parent URL substitution
    """

class CommentIdSubstitution(adapters.IdSubstitution, Mixin):
    """ Override context to be used for Id substitution
    """
