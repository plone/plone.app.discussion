""" Content rules handlers
"""
from plone.app.discussion import PloneAppDiscussionMessageFactory as _


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
    execute = lambda context, event: False


def execute_comment(event):
    """ Execute comment content rules
    """
    execute(event.object, event)

class CommentSubstitution(BaseSubstitution):
    """ Comment string substitution
    """
    def __init__(self, context, **kwargs):
        super(CommentSubstitution, self).__init__(context, **kwargs)
        self._session = None

    @property
    def session(self):
        """ User session
        """
        if self._session is None:
            sdm = getattr(self.context, 'session_data_manager', None)
            self._session = sdm.getSessionData(create=False) if sdm else {}
        return self._session

    @property
    def comment(self):
        """ Get changed inline comment
        """
        return self.session.get('comment', {})

class Id(CommentSubstitution):
    """ Comment id string substitution
    """
    category = _(u'Comments')
    description = _(u'Comment id')

    def safe_call(self):
        """ Safe call
        """
        return self.comment.get('comment_id', u'')

class Text(CommentSubstitution):
    """ Comment text
    """
    category = _(u'Comments')
    description = _(u'Comment text')

    def safe_call(self):
        """ Safe call
        """
        return self.comment.get('text', u'')

class AuthorUserName(CommentSubstitution):
    """ Comment author user name string substitution
    """
    category = _(u'Comments')
    description = _(u'Comment author user name')

    def safe_call(self):
        """ Safe call
        """
        return self.comment.get('author_username', u'')

class AuthorFullName(CommentSubstitution):
    """ Comment author full name string substitution
    """
    category = _(u'Comments')
    description = _(u'Comment author full name')

    def safe_call(self):
        """ Safe call
        """
        return self.comment.get('author_name', u'')

class AuthorEmail(CommentSubstitution):
    """ Comment author email string substitution
    """
    category = _(u'Comments')
    description = _(u'Comment author email')

    def safe_call(self):
        """ Safe call
        """
        return self.comment.get('author_email', u'')
