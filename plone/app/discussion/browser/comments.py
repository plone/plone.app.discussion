# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Acquisition import aq_inner
from datetime import datetime
from DateTime import DateTime
from plone.app.discussion import _
from plone.app.discussion.browser.validator import CaptchaValidator
from plone.app.discussion.interfaces import ICaptcha
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IReplies
from plone.app.layout.viewlets.common import ViewletBase
from plone.registry.interfaces import IRegistry
from plone.z3cform import z2
from plone.z3cform.fieldsets import extensible
from plone.z3cform.interfaces import IWrappedForm
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from urllib import quote as url_quote
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form import interfaces
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from z3c.form.interfaces import IFormLayer
from zope.component import createObject
from zope.component import queryUtility
from zope.i18n import translate
from zope.i18nmessageid import Message
from zope.interface import alsoProvides


COMMENT_DESCRIPTION_PLAIN_TEXT = _(
    u'comment_description_plain_text',
    default=u'You can add a comment by filling out the form below. '
            u'Plain text formatting.'
)

COMMENT_DESCRIPTION_MARKDOWN = _(
    u'comment_description_markdown',
    default=u'You can add a comment by filling out the form below. '
            u'Plain text formatting. You can use the Markdown syntax for '
            u'links and images.'
)

COMMENT_DESCRIPTION_INTELLIGENT_TEXT = _(
    u'comment_description_intelligent_text',
    default=u'You can add a comment by filling out the form below. '
            u'Plain text formatting. Web and email addresses are '
            u'transformed into clickable links.'
)

COMMENT_DESCRIPTION_MODERATION_ENABLED = _(
    u'comment_description_moderation_enabled',
    default=u'Comments are moderated.'
)


class CommentForm(extensible.ExtensibleForm, form.Form):

    ignoreContext = True  # don't use context to get widget data
    id = None
    label = _(u'Add a comment')
    fields = field.Fields(IComment).omit('portal_type',
                                         '__parent__',
                                         '__name__',
                                         'comment_id',
                                         'mime_type',
                                         'creator',
                                         'creation_date',
                                         'modification_date',
                                         'author_username',
                                         'title')

    def updateFields(self):
        super(CommentForm, self).updateFields()
        self.fields['user_notification'].widgetFactory = \
            SingleCheckBoxFieldWidget

    def updateWidgets(self):
        super(CommentForm, self).updateWidgets()

        # Widgets
        self.widgets['in_reply_to'].mode = interfaces.HIDDEN_MODE
        self.widgets['text'].addClass('autoresize')
        self.widgets['user_notification'].label = _(u'')
        # Reset widget field settings to their defaults, which may be changed
        # further on.  Otherwise, the email field might get set to required
        # when an anonymous user visits, and then remain required when an
        # authenticated user visits, making it impossible for an authenticated
        # user to fill in the form without validation error.  Or when in the
        # control panel the field is set as not required anymore, that change
        # would have no effect until the instance was restarted.  Note that the
        # widget is new each time, but the field is the same item in memory as
        # the previous time.
        self.widgets['author_email'].field.required = False
        # The widget is new, but its 'required' setting is based on the
        # previous value on the field, so we need to reset it here.  Changing
        # the field in updateFields does not help.
        self.widgets['author_email'].required = False

        # Rename the id of the text widgets because there can be css-id
        # clashes with the text field of documents when using and overlay
        # with TinyMCE.
        self.widgets['text'].id = 'form-widgets-comment-text'

        # Anonymous / Logged-in
        mtool = getToolByName(self.context, 'portal_membership')
        anon = mtool.isAnonymousUser()

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)

        if anon:
            if settings.anonymous_email_enabled:
                # according to IDiscussionSettings.anonymous_email_enabled:
                # 'If selected, anonymous user will have to give their email.'
                self.widgets['author_email'].field.required = True
                self.widgets['author_email'].required = True
            else:
                self.widgets['author_email'].mode = interfaces.HIDDEN_MODE
        else:
            self.widgets['author_name'].mode = interfaces.HIDDEN_MODE
            self.widgets['author_email'].mode = interfaces.HIDDEN_MODE

        member = mtool.getAuthenticatedMember()
        member_email = member.getProperty('email')

        # Hide the user_notification checkbox if user notification is disabled
        # or the user is not logged in. Also check if the user has a valid
        # email address
        member_email_is_empty = member_email == ''
        user_notification_disabled = not settings.user_notification_enabled
        if member_email_is_empty or user_notification_disabled or anon:
            self.widgets['user_notification'].mode = interfaces.HIDDEN_MODE

    def updateActions(self):
        super(CommentForm, self).updateActions()
        self.actions['cancel'].addClass('standalone')
        self.actions['cancel'].addClass('hide')
        self.actions['comment'].addClass('context')

    def get_author(self, data):
        context = aq_inner(self.context)
        # some attributes are not always set
        author_name = u''

        # Make sure author_name/ author_email is properly encoded
        if 'author_name' in data:
            author_name = data['author_name']
            if isinstance(author_name, str):
                author_name = unicode(author_name, 'utf-8')
        if 'author_email' in data:
            author_email = data['author_email']
            if isinstance(author_email, str):
                author_email = unicode(author_email, 'utf-8')

        # Set comment author properties for anonymous users or members
        portal_membership = getToolByName(context, 'portal_membership')
        anon = portal_membership.isAnonymousUser()
        if not anon and getSecurityManager().checkPermission(
                'Reply to item', context):
            # Member
            member = portal_membership.getAuthenticatedMember()
            # memberdata is stored as utf-8 encoded strings
            email = member.getProperty('email')
            fullname = member.getProperty('fullname')
            if not fullname or fullname == '':
                fullname = member.getUserName()
            elif isinstance(fullname, str):
                fullname = unicode(fullname, 'utf-8')
            author_name = fullname
            if email and isinstance(email, str):
                email = unicode(email, 'utf-8')
            # XXX: according to IComment interface author_email must not be
            # set for logged in users, cite:
            # 'for anonymous comments only, set to None for logged in comments'
            author_email = email
            # /XXX

        return author_name, author_email

    def create_comment(self, data):
        context = aq_inner(self.context)
        comment = createObject('plone.Comment')

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        anonymous_comments = settings.anonymous_comments

        # Set comment mime type to current setting in the discussion registry
        comment.mime_type = settings.text_transform

        # Set comment attributes (including extended comment form attributes)
        for attribute in self.fields.keys():
            setattr(comment, attribute, data[attribute])

        # Set dates
        comment.creation_date = datetime.utcnow()
        comment.modification_date = datetime.utcnow()

        # Get author name and email
        comment.author_name, comment.author_email = self.get_author(data)

        # Set comment author properties for anonymous users or members
        portal_membership = getToolByName(context, 'portal_membership')
        anon = portal_membership.isAnonymousUser()
        if anon and anonymous_comments:
            # Anonymous Users
            comment.user_notification = None
        elif not anon and getSecurityManager().checkPermission(
                'Reply to item', context):
            # Member
            member = portal_membership.getAuthenticatedMember()
            memberid = member.getId()
            user = member.getUser()
            comment.changeOwnership(user, recursive=False)
            comment.manage_setLocalRoles(memberid, ['Owner'])
            comment.creator = memberid
            comment.author_username = memberid

        else:  # pragma: no cover
            raise Unauthorized(
                u'Anonymous user tries to post a comment, but anonymous '
                u'commenting is disabled. Or user does not have the '
                u"'reply to item' permission."
            )

        return comment

    @button.buttonAndHandler(_(u'add_comment_button', default=u'Comment'),
                             name='comment')
    def handleComment(self, action):
        context = aq_inner(self.context)

        # Check if conversation is enabled on this content object
        if not self.__parent__.restrictedTraverse(
            '@@conversation_view'
        ).enabled():
            raise Unauthorized(
                'Discussion is not enabled for this content object.'
            )

        # Validation form
        data, errors = self.extractData()
        if errors:
            return

        # Validate Captcha
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        portal_membership = getToolByName(self.context, 'portal_membership')
        captcha_enabled = settings.captcha != 'disabled'
        anonymous_comments = settings.anonymous_comments
        anon = portal_membership.isAnonymousUser()
        if captcha_enabled and anonymous_comments and anon:
            if 'captcha' not in data:
                data['captcha'] = u''
            captcha = CaptchaValidator(self.context,
                                       self.request,
                                       None,
                                       ICaptcha['captcha'],
                                       None)
            captcha.validate(data['captcha'])

        # Create comment
        comment = self.create_comment(data)

        # Add comment to conversation
        conversation = IConversation(self.__parent__)
        if data['in_reply_to']:
            # Add a reply to an existing comment
            conversation_to_reply_to = conversation.get(data['in_reply_to'])
            replies = IReplies(conversation_to_reply_to)
            comment_id = replies.addComment(comment)
        else:
            # Add a comment to the conversation
            comment_id = conversation.addComment(comment)

        # Redirect after form submit:
        # If a user posts a comment and moderation is enabled, a message is
        # shown to the user that his/her comment awaits moderation. If the user
        # has 'review comments' permission, he/she is redirected directly
        # to the comment.
        can_review = getSecurityManager().checkPermission('Review comments',
                                                          context)
        workflowTool = getToolByName(context, 'portal_workflow')
        comment_review_state = workflowTool.getInfoFor(
            comment,
            'review_state',
            None
        )
        if comment_review_state == 'pending' and not can_review:
            # Show info message when comment moderation is enabled
            IStatusMessage(self.context.REQUEST).addStatusMessage(
                _('Your comment awaits moderator approval.'),
                type='info')
            self.request.response.redirect(self.action)
        else:
            # Redirect to comment (inside a content object page)
            self.request.response.redirect(self.action + '#' + str(comment_id))

    @button.buttonAndHandler(_(u'Cancel'))
    def handleCancel(self, action):
        # This method should never be called, it's only there to show
        # a cancel button that is handled by a jQuery method.
        pass  # pragma: no cover


class CommentsViewlet(ViewletBase):

    form = CommentForm
    index = ViewPageTemplateFile('comments.pt')

    def update(self):
        super(CommentsViewlet, self).update()
        discussion_allowed = self.is_discussion_allowed()
        anonymous_allowed_or_can_reply = (
            self.is_anonymous() and
            self.anonymous_discussion_allowed() or
            self.can_reply()
        )
        if discussion_allowed and anonymous_allowed_or_can_reply:
            z2.switch_on(self, request_layer=IFormLayer)
            self.form = self.form(aq_inner(self.context), self.request)
            alsoProvides(self.form, IWrappedForm)
            self.form.update()

    # view methods

    def can_reply(self):
        """Returns true if current user has the 'Reply to item' permission.
        """
        return getSecurityManager().checkPermission('Reply to item',
                                                    aq_inner(self.context))

    def can_manage(self):
        """We keep this method for <= 1.0b9 backward compatibility. Since we do
           not want any API changes in beta releases.
        """
        return self.can_review()

    def can_review(self):
        """Returns true if current user has the 'Review comments' permission.
        """
        return getSecurityManager().checkPermission('Review comments',
                                                    aq_inner(self.context))

    def can_delete_own(self, comment):
        """Returns true if the current user can delete the comment. Only
        comments without replies can be deleted.
        """
        try:
            return comment.restrictedTraverse(
                '@@delete-own-comment').can_delete()
        except Unauthorized:
            return False

    def could_delete_own(self, comment):
        """Returns true if the current user could delete the comment if it had
        no replies. This is used to prepare hidden form buttons for JS.
        """
        try:
            return comment.restrictedTraverse(
                '@@delete-own-comment').could_delete()
        except Unauthorized:
            return False

    def can_edit(self, reply):
        """Returns true if current user has the 'Edit comments'
        permission.
        """
        return getSecurityManager().checkPermission('Edit comments',
                                                    aq_inner(reply))

    def can_delete(self, reply):
        """Returns true if current user has the 'Delete comments'
        permission.
        """
        return getSecurityManager().checkPermission('Delete comments',
                                                    aq_inner(reply))

    def is_discussion_allowed(self):
        context = aq_inner(self.context)
        return context.restrictedTraverse('@@conversation_view').enabled()

    def comment_transform_message(self):
        """Returns the description that shows up above the comment text,
           dependent on the text_transform setting and the comment moderation
           workflow in the discussion control panel.
        """
        context = aq_inner(self.context)
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)

        # text transform setting
        if settings.text_transform == 'text/x-web-intelligent':
            message = translate(Message(COMMENT_DESCRIPTION_INTELLIGENT_TEXT),
                                context=self.request)
        elif settings.text_transform == 'text/x-web-markdown':
            message = translate(Message(COMMENT_DESCRIPTION_MARKDOWN),
                                context=self.request)
        else:
            message = translate(Message(COMMENT_DESCRIPTION_PLAIN_TEXT),
                                context=self.request)

        # comment workflow
        wftool = getToolByName(context, 'portal_workflow', None)
        workflow_chain = wftool.getChainForPortalType('Discussion Item')
        if workflow_chain:
            comment_workflow = workflow_chain[0]
            comment_workflow = wftool[comment_workflow]
            # check if the current workflow implements a pending state. If this
            # is true comments are moderated
            if 'pending' in comment_workflow.states:
                message = message + ' ' + \
                    translate(Message(COMMENT_DESCRIPTION_MODERATION_ENABLED),
                              context=self.request)

        return message

    def has_replies(self, workflow_actions=False):
        """Returns true if there are replies.
        """
        if self.get_replies(workflow_actions) is not None:
            try:
                self.get_replies(workflow_actions).next()
                return True
            except StopIteration:  # pragma: no cover
                pass
        return False

    def get_replies(self, workflow_actions=False):
        """Returns all replies to a content object.

        If workflow_actions is false, only published
        comments are returned.

        If workflow actions is true, comments are
        returned with workflow actions.
        """
        context = aq_inner(self.context)
        conversation = IConversation(context, None)

        if conversation is None:
            return iter([])

        wf = getToolByName(context, 'portal_workflow')
        # workflow_actions is only true when user
        # has 'Manage portal' permission

        def replies_with_workflow_actions():
            # Generator that returns replies dict with workflow actions
            for r in conversation.getThreads():
                comment_obj = r['comment']
                # list all possible workflow actions
                actions = [
                    a for a in wf.listActionInfos(object=comment_obj)
                    if a['category'] == 'workflow' and a['allowed']
                ]
                r = r.copy()
                r['actions'] = actions
                yield r

        def published_replies():
            # Generator that returns replies dict with workflow status.
            for r in conversation.getThreads():
                comment_obj = r['comment']
                workflow_status = wf.getInfoFor(comment_obj, 'review_state')
                if workflow_status == 'published':
                    r = r.copy()
                    r['workflow_status'] = workflow_status
                    yield r

        # Return all direct replies
        if len(conversation.objectIds()):
            if workflow_actions:
                return replies_with_workflow_actions()
            else:
                return published_replies()

    def get_commenter_home_url(self, username=None):
        if username is None:
            return None
        else:
            return '{0}/author/{1}'.format(self.context.portal_url(), username)

    def get_commenter_portrait(self, username=None):

        if username is None:
            # return the default user image if no username is given
            return 'defaultUser.png'
        else:
            portal_membership = getToolByName(self.context,
                                              'portal_membership',
                                              None)
            return portal_membership\
                .getPersonalPortrait(username)\
                .absolute_url()

    def anonymous_discussion_allowed(self):
        # Check if anonymous comments are allowed in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        return settings.anonymous_comments

    def edit_comment_allowed(self):
        # Check if editing comments is allowed in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        return settings.edit_comment_enabled

    def delete_own_comment_allowed(self):
        # Check if delete own comments is allowed in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        return settings.delete_own_comment_enabled

    def show_commenter_image(self):
        # Check if showing commenter image is enabled in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        return settings.show_commenter_image

    def is_anonymous(self):
        portal_membership = getToolByName(self.context,
                                          'portal_membership',
                                          None)
        return portal_membership.isAnonymousUser()

    def login_action(self):
        return '{0}/login_form?came_from={1}'.format(
            self.navigation_root_url,
            url_quote(self.request.get('URL', '')),
        )

    def format_time(self, time):
        # We have to transform Python datetime into Zope DateTime
        # before we can call toLocalizedTime.
        util = getToolByName(self.context, 'translation_service')
        zope_time = DateTime(time.isoformat())
        return util.toLocalizedTime(zope_time, long_format=True)
