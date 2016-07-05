# -*- coding: utf-8 -*-
"""The default comment class and factory.
"""
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_parent
from Acquisition import Implicit
from datetime import datetime
from OFS.owner import Owned
from OFS.role import RoleManager
from OFS.Traversable import Traversable
from persistent import Persistent
from plone.app.discussion import _
from plone.app.discussion.events import CommentAddedEvent
from plone.app.discussion.events import CommentRemovedEvent
from plone.app.discussion.events import ReplyAddedEvent
from plone.app.discussion.events import ReplyRemovedEvent
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry
from Products.CMFCore import permissions
from Products.CMFCore.CMFCatalogAware import CatalogAware
from Products.CMFCore.CMFCatalogAware import WorkflowAware
from Products.CMFCore.DynamicType import DynamicType
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.utils import safe_unicode
from smtplib import SMTPException
from zope.annotation.interfaces import IAnnotatable
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.factory import Factory
from zope.event import notify
from zope.i18n import translate
from zope.i18nmessageid import Message
from zope.interface import implementer

import logging


COMMENT_TITLE = _(
    u'comment_title',
    default=u'${author_name} on ${content}')

MAIL_NOTIFICATION_MESSAGE = _(
    u'mail_notification_message',
    default=u'A comment on "${title}" '
            u'has been posted here: ${link}\n\n'
            u'---\n'
            u'${text}\n'
            u'---\n')

MAIL_NOTIFICATION_MESSAGE_MODERATOR = _(
    u'mail_notification_message_moderator',
    default=u'A comment on "${title}" '
            u'has been posted here: ${link}\n\n'
            u'---\n'
            u'${text}\n'
            u'---\n\n'
            u'Approve comment:\n${link_approve}\n\n'
            u'Delete comment:\n${link_delete}\n')

logger = logging.getLogger('plone.app.discussion')


@implementer(IComment)
class Comment(CatalogAware, WorkflowAware, DynamicType, Traversable,
              RoleManager, Owned, Implicit, Persistent):
    """A comment.

    This object attempts to be as lightweight as possible. We implement a
    number of standard methods instead of subclassing, to have total control
    over what goes into the object.
    """
    security = ClassSecurityInfo()

    meta_type = portal_type = 'Discussion Item'
    # This needs to be kept in sync with types/Discussion_Item.xml title
    fti_title = 'Comment'

    __parent__ = None

    comment_id = None  # long
    in_reply_to = None  # long

    title = u''

    mime_type = None
    text = u''

    creator = None
    creation_date = None
    modification_date = None

    author_username = None

    author_name = None
    author_email = None

    user_notification = None

    # Note: we want to use zope.component.createObject() to instantiate
    # comments as far as possible. comment_id and __parent__ are set via
    # IConversation.addComment().

    def __init__(self):
        self.creation_date = self.modification_date = datetime.utcnow()
        self.mime_type = 'text/plain'

        user = getSecurityManager().getUser()
        if user and user.getId():
            aclpath = [x for x in user.getPhysicalPath() if x]
            self._owner = (aclpath, user.getId(),)
            self.__ac_local_roles__ = {
                user.getId(): ['Owner']
            }

    @property
    def __name__(self):
        return self.comment_id and unicode(self.comment_id) or None

    @property
    def id(self):
        return self.comment_id and str(self.comment_id) or None

    def getId(self):
        # The id of the comment, as a string.
        return self.id

    def getText(self, targetMimetype=None):
        # The body text of a comment.
        transforms = getToolByName(self, 'portal_transforms')

        if targetMimetype is None:
            targetMimetype = 'text/x-html-safe'

        sourceMimetype = getattr(self, 'mime_type', None)
        if sourceMimetype is None:
            registry = queryUtility(IRegistry)
            settings = registry.forInterface(IDiscussionSettings, check=False)
            sourceMimetype = settings.text_transform
        text = self.text
        if text is None:
            return ''
        if isinstance(text, unicode):
            text = text.encode('utf8')
        transform = transforms.convertTo(
            targetMimetype,
            text,
            context=self,
            mimetype=sourceMimetype)
        if transform:
            return transform.getData()
        else:
            logger = logging.getLogger('plone.app.discussion')
            msg = u'Transform "{0}" => "{1}" not available. Failed to ' \
                  u'transform comment "{2}".'
            logger.error(
                msg.format(sourceMimetype, targetMimetype, self.absolute_url())
            )
            return text

    def Title(self):
        # The title of the comment.

        if self.title:
            return self.title

        if not self.author_name:
            author_name = translate(
                Message(_(
                    u'label_anonymous',
                    default=u'Anonymous'
                ))
            )
        else:
            author_name = self.author_name

        # Fetch the content object (the parent of the comment is the
        # conversation, the parent of the conversation is the content object).
        content = aq_base(self.__parent__.__parent__)
        title = translate(
            Message(COMMENT_TITLE,
                    mapping={'author_name': safe_unicode(author_name),
                             'content': safe_unicode(content.Title())}))
        return title

    def Creator(self):
        # The name of the person who wrote the comment.
        return self.creator or self.author_name

    @security.protected(permissions.View)
    def Type(self):
        # The Discussion Item content type.
        return self.fti_title

    # CMF's event handlers assume any IDynamicType has these :(

    def opaqueItems(self):  # pragma: no cover
        return []

    def opaqueIds(self):  # pragma: no cover
        return []

    def opaqueValues(self):  # pragma: no cover
        return []

CommentFactory = Factory(Comment)


def notify_workflow(obj, event):
    """Tell the workflow tool when a comment is added
    """
    tool = getToolByName(obj, 'portal_workflow', None)
    if tool is not None:
        tool.notifyCreated(obj)


def notify_content_object(obj, event):
    """Tell the content object when a comment is added
    """
    content_obj = aq_parent(aq_parent(obj))
    content_obj.reindexObject(idxs=('total_comments',
                                    'last_comment_date',
                                    'commentators'))


def notify_content_object_deleted(obj, event):
    """Remove all comments of a content object when the content object has been
       deleted.
    """
    if IAnnotatable.providedBy(obj):
        conversation = IConversation(obj)
        while conversation:
            del conversation[conversation.keys()[0]]


def notify_comment_added(obj, event):
    """ Notify custom discussion events when a comment is added or replied
    """
    conversation = aq_parent(obj)
    context = aq_parent(conversation)
    if getattr(obj, 'in_reply_to', None):
        return notify(ReplyAddedEvent(context, obj))
    return notify(CommentAddedEvent(context, obj))


def notify_comment_removed(obj, event):
    """ Notify custom discussion events when a comment or reply is removed
    """
    conversation = aq_parent(obj)
    context = aq_parent(conversation)
    if getattr(obj, 'in_reply_to', None):
        return notify(ReplyRemovedEvent(context, obj))
    return notify(CommentRemovedEvent(context, obj))


def notify_content_object_moved(obj, event):
    """Update all comments of a content object that has been moved.
    """
    if event.oldParent is None or event.newParent is None \
            or event.oldName is None or event.newName is None:
        return

    # This method is also called for sublocations of moved objects. We
    # therefore can't assume that event.object == obj and event.
    # {old,new}{Parent,Name} may refer to the actually moved object further up
    # in the object hierarchy. The object is already moved at this point. so
    # obj.getPhysicalPath retruns the new path get the part of the path that
    # was moved.
    moved_path = obj.getPhysicalPath()[
        len(event.newParent.getPhysicalPath()) + 1:
    ]

    # Remove comments at the old location from catalog
    catalog = getToolByName(obj, 'portal_catalog')
    old_path = '/'.join(
        event.oldParent.getPhysicalPath() +
        (event.oldName,) +
        moved_path
    )
    brains = catalog.searchResults(dict(
        path={'query': old_path},
        portal_type='Discussion Item'
    ))
    for brain in brains:
        catalog.uncatalog_object(brain.getPath())
    # Reindex comment at the new location
    conversation = IConversation(obj, None)
    if conversation is not None:
        for comment in conversation.getComments():
            comment.reindexObject()


def notify_user(obj, event):
    """Tell users when a comment has been added.

       This method composes and sends emails to all users that have added a
       comment to this conversation and enabled user notification.

       This requires the user_notification setting to be enabled in the
       discussion control panel.
    """

    # Check if user notification is enabled
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)
    if not settings.user_notification_enabled:
        return

    # Get informations that are necessary to send an email
    mail_host = getToolByName(obj, 'MailHost')
    registry = getUtility(IRegistry)
    mail_settings = registry.forInterface(IMailSchema, prefix='plone')
    sender = mail_settings.email_from_address

    # Check if a sender address is available
    if not sender:
        return

    # Compose and send emails to all users that have add a comment to this
    # conversation and enabled user_notification.
    conversation = aq_parent(obj)
    content_object = aq_parent(conversation)

    # Avoid sending multiple notification emails to the same person
    # when he has commented multiple times.
    emails = set()
    for comment in conversation.getComments():
        obj_is_not_the_comment = obj != comment
        valid_user_email = comment.user_notification and comment.author_email
        if obj_is_not_the_comment and valid_user_email:
            emails.add(comment.author_email)

    if not emails:
        return

    subject = translate(_(u'A comment has been posted.'),
                        context=obj.REQUEST)
    message = translate(
        Message(
            MAIL_NOTIFICATION_MESSAGE,
            mapping={
                'title': safe_unicode(content_object.title),
                'link': content_object.absolute_url() + '/view#' + obj.id,
                'text': obj.text
            }
        ),
        context=obj.REQUEST
    )
    for email in emails:
        # Send email
        try:
            mail_host.send(message,
                           email,
                           sender,
                           subject,
                           charset='utf-8')
        except SMTPException:
            logger.error('SMTP exception while trying to send an ' +
                         'email from %s to %s',
                         sender,
                         email)


def notify_moderator(obj, event):
    """Tell the moderator when a comment needs attention.

       This method sends an email to the moderator if comment moderation a new
       comment has been added that needs to be approved.

       The moderator_notification setting has to be enabled in the discussion
       control panel.

       Configure the moderator e-mail address in the discussion control panel.
       If no moderator is configured but moderator notifications are turned on,
       the site admin email (from the mail control panel) will be used.
    """
    # Check if moderator notification is enabled
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)
    if not settings.moderator_notification_enabled:
        return

    # Get informations that are necessary to send an email
    mail_host = getToolByName(obj, 'MailHost')
    registry = getUtility(IRegistry)
    mail_settings = registry.forInterface(IMailSchema, prefix='plone')
    sender = mail_settings.email_from_address

    if settings.moderator_email:
        mto = settings.moderator_email
    else:
        mto = sender

    # Check if a sender address is available
    if not sender:
        return

    conversation = aq_parent(obj)
    content_object = aq_parent(conversation)

    # Compose email
    subject = translate(_(u'A comment has been posted.'), context=obj.REQUEST)
    link_approve = obj.absolute_url() + '/@@moderate-publish-comment'
    link_delete = obj.absolute_url() + '/@@moderate-delete-comment'
    message = translate(
        Message(
            MAIL_NOTIFICATION_MESSAGE_MODERATOR,
            mapping={
                'title': safe_unicode(content_object.title),
                'link': content_object.absolute_url() + '/view#' + obj.id,
                'text': obj.text,
                'link_approve': link_approve,
                'link_delete': link_delete,
            }
        ),
        context=obj.REQUEST
    )

    # Send email
    try:
        mail_host.send(message, mto, sender, subject, charset='utf-8')
    except SMTPException, e:
        logger.error('SMTP exception (%s) while trying to send an ' +
                     'email notification to the comment moderator ' +
                     '(from %s to %s, message: %s)',
                     e,
                     sender,
                     mto,
                     message)
