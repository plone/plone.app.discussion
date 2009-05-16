from zope.interface import Interface
from zope.interface.common.mapping import IIterableMapping, IWriteMapping
from zope import schema

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('plone.app.discussion')

class IDiscussionSettings(Interface):
    """Global discussion settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    globally_enabled = schema.Bool(title=_(u"Globally enabled"),
                                   description=_(u"Use this setting to enable or disable comments globally"),
                                   default=True)
    
    index_comments = schema.Bool(title=_(u"Index comments"),
                                 description=_(u"Enable this option to ensure that comments are searchable. "
                                                "Turning this off may improve performance for sites with large "
                                                "volumes of comments that do not wish to make them searcahble using "
                                                "the standard search tools."),
                                 default=True)

class IConversation(IIterableMapping, IWriteMapping):
    """A conversation about a content object.
    
    This is a persistent object in its own right and manages all comments.
    
    The dict interface allows access to all comments. They are stored by
    integer key, in the order they were added.
    
    To get replies at the top level, adapt the conversation to IReplies.
    
    The conversation can be traversed to via the ++comments++ namespace.
    For example, path/to/object/++comments++/123 retrieves comment 123.
    
    The __parent__ of the conversation (and the acquisition parent during
    traversal) is the content object. The conversation is the __parent__
    (and acquisition parent) for all comments, regardless of threading.
    """
    
    enabled = schema.Bool(title=_(u"Is commenting enabled?"))
    
    total_comments = schema.Int(title=_(u"Total number of comments on this item"), min=0, readonly=True)
    last_comment_date = schema.Date(title=_(u"Date of the most recent comment"), readonly=True)
    commentators = schema.Set(title=_(u"The set of unique commentators (usernames)"), readonly=True)
    
    def getComments(start=0, size=None):
        """Return a batch of comment objects for rendering. The 'start'
        parameter is the id of the comment from which to start the batch.
        The 'size' parameter is the number of comments to return in the
        batch.
        
        The comments are returned in creation date order, in the exact batche
        size specified.
        """
    
    def getThreads(start=0, size=None, root=None, depth=None):
        """Return a batch of comment objects for rendering. The 'start'
        parameter is the id of the comment from which to start the batch.
        The 'size' parameter is the number of comments to return in the
        batch. 'root', if given, is the id of the comment to which reply
        threads will be found. If not given, all threads are returned.
        If 'depth' is given, it can be used to limit the depth of threads
        returned. For example, depth=1 will return only direct replies.
        
        Comments are returned as a recursive list of '(comment, children)', 
        where 'children' is a similar list of (comment, children), or an empty
        list of a comment has no direct replies.
        
        The returned number of comments may be bigger than the batch size,
        in order to give enough context to show the full  lineage of the
        starting comment.
        """
        
    def addComment(comment):
        """Adds a new comment to the list of comments, and returns the 
        comment id that was assigned.
        """

class IReplies(IIterableMapping, IWriteMapping):
    """A set of related comments in reply to a given content object or
    another comment.
    
    Adapt a conversation or another comment to this interface to obtain the
    direct replies.
    """

class IComment(Interface):
    """A comment.
    
    Comments are indexed in the catalog and subject to workflow and security.
    """

    portal_type = schema.ASCIILine(title=_(u"Portal type"), default="Discussion Item")
    
    __parent__ = schema.Object(title=_(u"Conversation"), schema=Interface)
    __name__ = schema.TextLine(title=_(u"Name"))
    
    comment_id = schema.Int(title=_(u"A comment id unique to this conversation"))
    in_reply_to = schema.Int(title=_(u"Id of comment this comment is in reply to"), required=False)
    
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
