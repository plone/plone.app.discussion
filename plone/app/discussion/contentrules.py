# -*- coding: utf-8 -*-
""" Content rules handlers
"""
from plone.app.discussion import _


try:
    from plone.stringinterp.adapters import BaseSubstitution
except ImportError:
    class BaseSubstitution(object):
        """ Fallback class if plone.stringinterp is not available
        """

        def __init__(self, context, **kwargs):
            self.context = context

try:
    from plone.app.contentrules.handlers import execute
except ImportError:
    def execute(context, event):
        return False


def execute_comment(event):
    """ Execute comment content rules
    """
    execute(event.object, event)


class CommentSubstitution(BaseSubstitution):
    """ Comment string substitution
    """

    def __init__(self, context, **kwargs):
        super(CommentSubstitution, self).__init__(context, **kwargs)

    @property
    def event(self):
        """ event that triggered the content rule
        """
        return self.context.REQUEST.get('event')

    @property
    def comment(self):
        """ Get changed inline comment
        """
        return self.event.comment


class Id(CommentSubstitution):
    """ Comment id string substitution
    """
    category = _(u'Comments')
    description = _(u'Comment id')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.comment, 'comment_id', u'')


class Text(CommentSubstitution):
    """ Comment text
    """
    category = _(u'Comments')
    description = _(u'Comment text')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.comment, 'text', u'')


class AuthorUserName(CommentSubstitution):
    """ Comment author user name string substitution
    """
    category = _(u'Comments')
    description = _(u'Comment author user name')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.comment, 'author_username', u'')


class AuthorFullName(CommentSubstitution):
    """ Comment author full name string substitution
    """
    category = _(u'Comments')
    description = _(u'Comment author full name')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.comment, 'author_name', u'')


class AuthorEmail(CommentSubstitution):
    """ Comment author email string substitution
    """
    category = _(u'Comments')
    description = _(u'Comment author email')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.comment, 'author_email', u'')
