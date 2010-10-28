# -*- coding: utf-8 -*-
from Acquisition import aq_inner

from AccessControl import Unauthorized
from AccessControl import getSecurityManager

from datetime import datetime
from DateTime import DateTime

from urllib import quote as url_quote

from zope.component import createObject, queryUtility

from zope.interface import alsoProvides

from z3c.form import form, field, button, interfaces
from z3c.form.interfaces import IFormLayer

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from plone.registry.interfaces import IRegistry

from plone.app.layout.viewlets.common import ViewletBase

from plone.app.discussion import PloneAppDiscussionMessageFactory as _
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IReplies
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import ICaptcha

from plone.app.discussion.browser.validator import CaptchaValidator

from plone.z3cform import z2
from plone.z3cform.fieldsets import extensible

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface 
try:
    from plone.z3cform.interfaces import IWrappedForm 
    HAS_WRAPPED_FORM = True 
except ImportError: # pragma: no cover
    HAS_WRAPPED_FORM = False


class CommentForm(extensible.ExtensibleForm, form.Form):

    ignoreContext = True # don't use context to get widget data
    id = None
    label = _(u"Add a comment")
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
        #self.fields['author_notification'].widgetFactory = 
        #    SingleCheckBoxFieldWidget

    def updateWidgets(self):
        super(CommentForm, self).updateWidgets()

        # Widgets
        self.widgets['in_reply_to'].mode = interfaces.HIDDEN_MODE
        self.widgets['text'].addClass("autoresize")
        #self.widgets['author_notification'].label = _(u"")   
        
        # Anonymous / Logged-in
        portal_membership = getToolByName(self.context, 'portal_membership')
        if not portal_membership.isAnonymousUser():
            self.widgets['author_name'].mode = interfaces.HIDDEN_MODE
            self.widgets['author_email'].mode = interfaces.HIDDEN_MODE

        # XXX: Since we are not using the author_email field in the 
        # current state, we hide it by default. But we keep the field for 
        # integrators or later use. 
        self.widgets['author_email'].mode = interfaces.HIDDEN_MODE
         
        # XXX: Author notification code
        #registry = queryUtility(IRegistry)
        #settings = registry.forInterface(IDiscussionSettings)
        #if not settings.user_notification_enabled:
        #    self.widgets['author_notification'].mode = interfaces.HIDDEN_MODE
        
    def updateActions(self):
        super(CommentForm, self).updateActions()        
        self.actions['cancel'].addClass("standalone")
        self.actions['cancel'].addClass("hide")  
        self.actions['comment'].addClass("context")  
        
    @button.buttonAndHandler(_(u"add_comment_button", default=u"Comment"), 
                             name='comment')
    def handleComment(self, action):
        context = aq_inner(self.context)
        wf = getToolByName(context, 'portal_workflow')
        
        data, errors = self.extractData()
        if errors:
            return

        text = u""
        author_name = u""
        author_email = u""
        #author_notification = None

        # Captcha check for anonymous users (if Captcha is enabled and 
        # anonymous commenting is allowed)
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        portal_membership = getToolByName(self.context, 'portal_membership')
        if settings.captcha != 'disabled' and \
        settings.anonymous_comments and \
        portal_membership.isAnonymousUser():
            if not 'captcha' in data:
                data['captcha'] = u""
            captcha = CaptchaValidator(self.context, 
                                       self.request, 
                                       None, 
                                       ICaptcha['captcha'], 
                                       None)
            captcha.validate(data['captcha'])

        # Fetch data from request
        if 'text' in data:
            text = data['text']
        if 'author_name' in data:
            author_name = data['author_name']
        if 'author_email' in data:
            author_email = data['author_email']
        #if 'author_notification' in data:
        #    author_notification = data['author_notification']
            
        # The add-comment view is called on the conversation object
        conversation = IConversation(self.__parent__)
        
        # Check if conversation is enabled on this content object
        if not conversation.enabled():
            raise Unauthorized, "Discussion is not enabled for this content\
                                 object."

        if data['in_reply_to']:
            # Fetch the comment we want to reply to
            conversation_to_reply_to = conversation.get(data['in_reply_to'])
            replies = IReplies(conversation_to_reply_to)

        # Create the comment
        comment = createObject('plone.Comment')
        comment.text = text

        portal_membership = getToolByName(self.context, 'portal_membership')

        if portal_membership.isAnonymousUser() and \
        settings.anonymous_comments:
            # Anonymous Users
            comment.creator = author_name
            comment.author_name = author_name
            comment.author_email = author_email
            #comment.author_notification = author_notification
            comment.creation_date = comment.modification_date = datetime.utcnow()
        elif not portal_membership.isAnonymousUser():
            # Member
            member = portal_membership.getAuthenticatedMember()
            username = member.getUserName()
            email = member.getProperty('email')
            fullname = member.getProperty('fullname')
            if not fullname or fullname == '':
                fullname = member.getUserName()
            # memberdata is stored as utf-8 encoded strings
            elif isinstance(fullname, str):
                fullname = unicode(fullname, 'utf-8')
            if email and isinstance(email, str):
                email = unicode(email, 'utf-8')
            comment.creator = fullname
            comment.author_username = username
            comment.author_name = fullname
            comment.author_email = email
            #comment.author_notification = comment.author_notification
            comment.creation_date = comment.modification_date = datetime.utcnow()
        else:
            raise Unauthorized, "Anonymous user tries to post a comment, but \
                                 anonymous commenting is disabled." # pragma: no cover
        
        # Check if the added comment is a reply to an existing comment
        # or just a regular reply to the content object.
        if data['in_reply_to']:
            # Add a reply to an existing comment
            comment_id = replies.addComment(comment)
        else:
            # Add a comment to the conversation
            comment_id = conversation.addComment(comment)

        # If a user posts a comment and moderation is enabled, a message is 
        # shown to the user that his/her comment awaits moderation. If the user 
        # has manage right, he/she is redirected directly to the comment.
        can_manage = getSecurityManager().checkPermission('Manage portal', 
                                                          context)
        comment_review_state = wf.getInfoFor(comment, 'review_state')
        if comment_review_state == 'pending' and not can_manage:
            # Show info message when comment moderation is enabled
            IStatusMessage(self.context.REQUEST).addStatusMessage(
                _("Your comment awaits moderator approval."),
                type="info")
            self.request.response.redirect(self.action)
        else:
            # Redirect to comment (inside a content object page)
            self.request.response.redirect(self.action + '#' + str(comment_id))

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        # This method should never be called, it's only there to show
        # a cancel button that is handled by a jQuery method.
        pass # pragma: no cover


class CommentsViewlet(ViewletBase):

    form = CommentForm
    index = ViewPageTemplateFile('comments.pt')

    def update(self):
        super(CommentsViewlet, self).update()
        z2.switch_on(self, request_layer=IFormLayer)
        self.form = self.form(aq_inner(self.context), self.request)
        if HAS_WRAPPED_FORM: 
            alsoProvides(self.form, IWrappedForm) 
        self.form.update()

    # view methods

    def cook(self, text):
        transforms = getToolByName(self, 'portal_transforms')
        targetMimetype = 'text/html'
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        mimetype = settings.text_transform        
        return transforms.convertTo(targetMimetype, 
                                    text, 
                                    context=self, 
                                    mimetype=mimetype).getData()
    
    def can_reply(self):
        """Returns true if current user has the 'Reply to item' permission.
        """        
        return getSecurityManager().checkPermission('Reply to item', 
                                                    aq_inner(self.context))

    def can_review(self):
        """Returns true if current user has the 'Review comments' permission.
        """
        return getSecurityManager().checkPermission('Review comments', 
                                                    aq_inner(self.context))
        
    def is_discussion_allowed(self):
        context = aq_inner(self.context)
        conversation = IConversation(context)
        return conversation.enabled()

    def has_replies(self, workflow_actions=False):
        """Returns true if there are replies.
        """
        if self.get_replies(workflow_actions) is not None:
            try:
                self.get_replies(workflow_actions).next()
                return True
            except StopIteration: # pragma: no cover
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
        conversation = IConversation(context)

        wf = getToolByName(context, 'portal_workflow')

        # workflow_actions is only true when user
        # has 'Manage portal' permission

        def replies_with_workflow_actions():
            # Generator that returns replies dict with workflow actions
            for r in conversation.getThreads():
                comment_obj = r['comment']
                # list all possible workflow actions
                actions = [a for a in wf.listActionInfos(object=comment_obj)
                               if a['category'] == 'workflow' and a['allowed']]
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
        if conversation.total_comments > 0:
            if workflow_actions:
                return replies_with_workflow_actions()
            else:
                return published_replies()

    def get_commenter_home_url(self, username=None):
        if username is None:
            return None
        else:
            return "%s/author/%s" % (self.context.portal_url(), username)

    def get_commenter_portrait(self, username=None):

        if username is None:
            # return the default user image if no username is given
            return 'defaultUser.gif'
        else:
            portal_membership = getToolByName(self.context,
                                              'portal_membership',
                                              None)
            return portal_membership.getPersonalPortrait(username)\
                   .absolute_url()

    def anonymous_discussion_allowed(self):
        # Check if anonymous comments are allowed in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        return settings.anonymous_comments

    def show_commenter_image(self):
        # Check if showing commenter image is enabled in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        return settings.show_commenter_image

    def is_anonymous(self):
        portal_membership = getToolByName(self.context, 
                                          'portal_membership', 
                                          None)
        return portal_membership.isAnonymousUser()
    
    def login_action(self):
        return '%s/login_form?came_from=%s' % \
            (self.navigation_root_url,
             url_quote(self.request.get('URL', '')),)

    def format_time(self, time):
        # We have to transform Python datetime into Zope DateTime
        # before we can call toLocalizedTime.
        util = getToolByName(self.context, 'translation_service')
        zope_time = DateTime(time.isoformat())
        return util.toLocalizedTime(zope_time, long_format=True)
