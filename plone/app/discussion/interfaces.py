# -*- coding: utf-8 -*-
"""Interfaces for plone.app.discussion
"""

from zope.interface import Interface
from zope.interface.common.mapping import IIterableMapping
from zope import schema

from plone.app.discussion import PloneAppDiscussionMessageFactory as _


class IDiscussionSettings(Interface):
    """Global discussion settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    # Todo: Write a short hint, that other discussion related options can
    # be found elsewhere in the Plone control panel:
    #
    # - Types control panel: Allow comments on content types
    # - Search control panel: Show comments in search results

    globally_enabled = schema.Bool(
        title=_(u"label_globally_enabled",
                default=u"Globally enable comments"),
        description=_(u"help_globally_enabled",
                default=u"If selected, users are able to post comments on the "
                         "site. Though, you have to enable comments for "
                         "specific content types, folders or content objects "
                         "before users will be able to post comments."),
        required=False,
        default=False,
        )

    anonymous_comments = schema.Bool(
        title=_(u"label_anonymous_comments",
                default="Enable anonymous comments"),
        description=_(u"help_anonymous_comments",
                default=u"If selected, anonymous users are able to post "
                         "comments without loggin in. It is highly "
                         "recommended to use a captcha solution to prevent "
                         "spam if this setting is enabled."),
        required=False,
        default=False,
        )

    moderation_enabled = schema.Bool(
        title=_(u"label_moderation_enabled",
                default="Enable comment moderation"),
        description=_(u"help_moderation_enabled",
                default=u"If selected, comments will enter a 'Pending' state "
                         "in which they are invisible to the public. A user "
                         "with the 'Review comments' permission ('Reviewer' "
                         "or 'Manager') can approve comments to make them "
                         "visible to the public. If you want to enable a "
                         "custom comment workflow, you have to go to the "
                         "types control panel."),
        required=False,
        default=False,
        )

    text_transform = schema.Choice(
        title=_(u"label_text_transform",
                default="Comment text transform"),
        description=_(u"help_text_transform",
                default=u"Use this setting to choose if the comment text " +
                         "should be transformed in any way. You can choose "
                         "between 'Plain text' and 'Intelligent text'. " +
                         "'Intelligent text' converts plain text into HTML " +
                         "where line breaks and indentation is preserved, " +
                         "and web and email addresses are made into " +
                         "clickable links."),
        required=True,
        default='text/plain',
        vocabulary='plone.app.discussion.vocabularies.TextTransformVocabulary',
        )

    captcha = schema.Choice(
        title=_(u"label_captcha",
                default="Captcha"),
        description=_(u"help_captcha",
                default=u"Use this setting to enable or disable Captcha "
                         "validation for comments. Install "
                         "plone.formwidget.captcha, "
                         "plone.formwidget.recaptcha, collective.akismet, or "
                         "collective.z3cform.norobots if there are no options "
                         "available."),
        required=True,
        default='disabled',
        vocabulary='plone.app.discussion.vocabularies.CaptchaVocabulary',
        )

    show_commenter_image = schema.Bool(
        title=_(u"label_show_commenter_image",
                default=u"Show commenter image"),
        description=_(u"help_show_commenter_image",
                default=u"If selected, an image of the user is shown next to "
                         "the comment."),
        required=False,
        default=True,
        )

    moderator_notification_enabled = schema.Bool(
        title=_(u"label_moderator_notification_enabled",
                default=u"Enable moderator email notification"),
        description=_(u"help_moderator_notification_enabled",
                default=u"If selected, the moderator is notified if a comment "
                         "needs attention. The moderator email address can " +
                         "be found in the 'Mail settings' control panel "
                         "(Site 'From' address)"),
        required=False,
        default=False,
        )

    moderator_email = schema.ASCIILine(
        title=_(u'label_moderator_email',
                  default=u'Moderator Email Address'),
        description=_(u'help_moderator_email',
                      default=u"Address to which moderator notifications "
                              u"will be sent."),
        required=False,
        )

    user_notification_enabled = schema.Bool(
        title=_(u"label_user_notification_enabled",
        default=u"Enable user email notification"),
        description=_(u"help_user_notification_enabled",
                      default=u"If selected, users can choose to be notified "
                               "of new comments by email."),
        required=False,
        default=False)


class IConversation(IIterableMapping):
    """A conversation about a content object.

    This is a persistent object in its own right and manages all comments.

    The dict interface allows access to all comments. They are stored by
    long integer key, in the order they were added.

    Note that __setitem__() is not supported - use addComment() instead.
    However, comments can be deleted using __delitem__().

    To get replies at the top level, adapt the conversation to IReplies.

    The conversation can be traversed to via the ++comments++ namespace.
    For example, path/to/object/++comments++/123 retrieves comment 123.

    The __parent__ of the conversation (and the acquisition parent during
    traversal) is the content object. The conversation is the __parent__
    (and acquisition parent) for all comments, regardless of threading.
    """

    total_comments = schema.Int(
        title=_(u"Total number of comments on this item"),
        min=0,
        readonly=True,
        )

    last_comment_date = schema.Date(
        title=_(u"Date of the most recent comment"),
        readonly=True,
        )

    commentators = schema.Set(
        title=_(u"The set of unique commentators (usernames)"),
        readonly=True,
        )

    def addComment(comment):
        """Adds a new comment to the list of comments, and returns the
        comment id that was assigned. The comment_id property on the comment
        will be set accordingly.
        """

    def __delitem__(key):
        """Delete the comment with the given key. The key is a long id.
        """

    def getComments(start=0, size=None):
        """Return an iterator of comment objects for rendering.

        The 'start' parameter is the id of the comment from which to start the
        batch. If no such comment exists, the next higher id will be used.
        This means that you can use max key from a previous batch + 1 safely.

        The 'size' parameter is the number of comments to return in the
        batch.

        The comments are returned in creation date order, in the exact batch
        size specified.
        """

    def getThreads(start=0, size=None, root=0, depth=None):
        """Return a batch of comment objects for rendering.

        The 'start' parameter is the id of the comment from which to start
        the batch. If no such comment exists, the next higher id will be used.
        This means that you can use max key from a previous batch + 1 safely.
        This should be a root level comment.

        The 'size' parameter is the number of threads to return in the
        batch. Full threads are always returned (although you can stop
        consuming the iterator if you want to abort).

        'root', if given, is the id of the comment to which reply
        threads will be found. 'root' itself is not included. If not given,
        all threads are returned.

        If 'depth' is given, it can be used to limit the depth of threads
        returned. For example, depth=1 will return only direct replies.

        Comments are returned as an iterator of dicts with keys 'comment',
        the comment, 'id', the comment id, and 'depth', which is 0 for
        top-level comments, 1 for their replies, and so on. The list is
        returned in depth-first order.
        """


class IReplies(IIterableMapping):
    """A set of related comments in reply to a given content object or
    another comment.

    Adapt a conversation or another comment to this interface to obtain the
    direct replies.
    """

    def addComment(comment):
        """Adds a new comment as a child of this comment, and returns the
        comment id that was assigned. The comment_id property on the comment
        will be set accordingly.
        """

    def __delitem__(key):
        """Delete the comment with the given key. The key is a long id.
        """


class IComment(Interface):
    """A comment.

    Comments are indexed in the catalog and subject to workflow and security.
    """

    portal_type = schema.ASCIILine(
        title=_(u"Portal type"),
        default="Discussion Item",
        )

    __parent__ = schema.Object(
        title=_(u"Conversation"), schema=Interface)

    __name__ = schema.TextLine(title=_(u"Name"))

    comment_id = schema.Int(
        title=_(u"A comment id unique to this conversation"))

    in_reply_to = schema.Int(
        title=_(u"Id of comment this comment is in reply to"),
        required=False,
        )

    # for logged in comments - set to None for anonymous
    author_username = schema.TextLine(title=_(u"Name"), required=False)

    # for anonymous comments only, set to None for logged in comments
    author_name = schema.TextLine(title=_(u"Name"), required=False)
    author_email = schema.TextLine(title=_(u"Email"), required=False)

    title = schema.TextLine(title=_(u"label_subject",
                                    default=u"Subject"))

    mime_type = schema.ASCIILine(title=_(u"MIME type"), default="text/plain")
    text = schema.Text(title=_(u"label_comment",
                               default=u"Comment"))

    user_notification = schema.Bool(title=_(u"Notify me of new comments via "
                                             "email."),
                                     required=False)

    creator = schema.TextLine(title=_(u"Author name (for display)"))
    creation_date = schema.Date(title=_(u"Creation date"))
    modification_date = schema.Date(title=_(u"Modification date"))


class ICaptcha(Interface):
    """Captcha/ReCaptcha text field to extend the existing comment form.
    """
    captcha = schema.TextLine(title=u"Captcha",
                              required=False)


class ICommentingTool(Interface):
    """A tool that indexes all comments for usage by the management interface.

    This means the management interface can still work even though we don't
    index the comments in portal_catalog.

    The default implementation of this interface simply defers to
    portal_catalog, but a custom version of the tool can be used to provide
    an alternate indexing mechanism.
    """

    def indexObject(comment):
        """Indexes a comment
        """

    def reindexObject(comment):
        """Reindex a comment
        """

    def unindexObject(comment):
        """Removes a comment from the indexes
        """

    def uniqueValuesFor(name):
        """Get unique values for FieldIndex name
        """

    def searchResults(REQUEST=None, **kw):
        """Perform a search over all indexed comments.
        """


class IDiscussionLayer(Interface):
    """Request marker installed via browserlayer.xml.
    """
