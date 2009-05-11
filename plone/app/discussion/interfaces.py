from zope.interface import Interface
from zope.interface.common.mapping import IIterableMapping, IWriteMapping
from zope import schema

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('plone.app.discussion')

class IReplies(IIterableMapping, IWriteMapping):
    """A set of related comments
    
    This acts as a mapping (dict) with string keys and values being other
    discussion items in reply to this discussion item.
    """

class IHasReplies(Interface):
    """Common interface for objects that have replies.
    """

    replies = schema.Object(title=_(u"Replies"), schema=IReplies)

class IComment(IHasReplies):
    """A comment
    """

    portal_type = schema.ASCIILine(title=_(u"Portal type"), default="Discussion Item")
    
    __parent__ = schema.Object(title=_(u"In reply to"), description=_(u"Another comment or a content item"), schema=Interface)
    __name__ = schema.TextLine(title=_(u"Name"))
    
    ancestor = schema.Object(title=_(u"The original content object the comment is for"), schema=Interface)
    
    title = schema.TextLine(title=_(u"Subject"))
    
    mime_type = schema.ASCIILine(title=_(u"MIME type"), default="text/plain")
    text = schema.Text(title=_(u"Comment text"))
    
    creator = schema.TextLine(title=_(u"Author name (for display)"))
    creation_date = schema.Date(title=_(u"Creation date"))
    modification_date = schema.Date(title=_(u"Modification date"))

    # for logged in comments - set to None for anonymous
    author_username = schema.TextLine(title=_(u"Author username"), required=False)
    
    # for anonymous comments only, set to None for logged in comments
    author_name = schema.TextLine(title=_(u"Author name"), required=False)
    author_email = schema.TextLine(title=_(u"Author email address"), required=False)

class IDiscussable(IHasReplies):
    """Adapt a content item to this interface to determine whether discussions
    are currently enabled, and obtain a list of comments.
    """
    
    enabled = schema.Bool(title=_(u"Is commenting enabled?"))
    
    total_comments = schema.Int(title=_(u"Total number of comments on this item"), min=0, readonly=True)
    last_comment_date = schema.Date(title=_(u"Date of the most recent comment"), readonly=True)
    commentators = schema.Set(title=_(u"The set of unique commentators (usernames)"), readonly=True)

class IDiscussionSettings(Interface):
    """Global discussion settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    globally_enabled = schema.Bool(title=_(u"Globally enabled"),
                                   description=_(u"Use this setting to enable or disable comments globally"),
                                   default=True)

