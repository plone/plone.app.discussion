### OLD ###

from datetime import datetime
from DateTime import DateTime

from urllib import quote as url_quote

from zope.interface import implements

from zope.component import createObject, getMultiAdapter, queryUtility

from zope.viewlet.interfaces import IViewlet

from Acquisition import aq_inner, aq_parent, aq_base

from AccessControl import getSecurityManager

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

from plone.registry.interfaces import IRegistry

from plone.app.layout.viewlets.common import ViewletBase

from plone.app.discussion.comment import CommentFactory
from plone.app.discussion.interfaces import IConversation, IComment, IReplies, IDiscussionSettings

### NEW ###

from plone.app.layout.viewlets.common import ViewletBase

from zope.interface import Interface, implements

from zope.viewlet.interfaces import IViewlet

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.z3cform import layout

from zope import interface, schema
from z3c.form import form, field, button, interfaces
from plone.z3cform.layout import wrap_form

from plone.z3cform import z2

from plone.app.discussion.interfaces import IComment

from zope.annotation import IAttributeAnnotatable

from plone.z3cform.fieldsets import extensible

from Products.Five.browser import BrowserView

from zope.schema.fieldproperty import FieldProperty

class View(BrowserView):
    """Comment View
    """

    def __call__(self):
        # Redirect from /path/to/object/++conversation++default/123456789
        # to /path/to/object#comment-123456789
        comment_id = aq_parent(self).id
        #self.request.response.redirect(aq_parent(aq_parent(aq_parent(self))).absolute_url() + '#comment-' + comment_id)
        self.request.response.redirect(aq_parent(aq_parent(aq_parent(self))).absolute_url() + '#' + comment_id)


class Comment(object):
    implements(IComment, IAttributeAnnotatable)
    portal_type = u""
    __parent__ = None
    __name__ = None
    comment_id = u""
    in_reply_to = u""
    title = u""
    mime_type = u""
    text = u""
    creator = u""
    creation_date = u""
    modification_date = u""
    author_username = u""
    author_name = u""
    author_email = u""

class CommentForm(extensible.ExtensibleForm, form.Form):

    ignoreContext = True # don't use context to get widget data
    label = u"Add a comment"

    @button.buttonAndHandler(u'Post comment')
    def handleApply(self, action):
        data, errors = self.extractData()
        print data['title'] # ... or do stuff

    @property
    def fields(self):
        title = FieldProperty(IComment['title'])
        text = FieldProperty(IComment['text'])
        return field.Fields(title, text)

class ViewletFormWrapper(ViewletBase, layout.FormWrapper):

    implements(IViewlet)

    form = CommentForm
    label = 'Add Comment'

    index = ViewPageTemplateFile('comments.pt')

    #def index(self):
    #    return ViewPageTemplateFile('comments.pt').__of__(self)(self)

    def __init__(self, context, request, view, manager):
        super(ViewletFormWrapper, self).__init__(context, request, view, manager)
        if self.form is not None:
            self.form_instance = self.form(self.context.aq_inner, self.request)
            self.form_instance.__name__ = self.__name__

        self.portal_discussion = getToolByName(self.context, 'portal_discussion', None)
        self.portal_membership = getToolByName(self.context, 'portal_membership', None)

    #def contents(self):
    #    """This is the method that'll call your form.  You don't
    #    usually override this.
    #    """
    #    # A call to 'switch_on' is required before we can render
    #    # z3c.forms within Zope 2.
    #    z2.switch_on(self, request_layer=self.request_layer)
    #    return self.render_form()

    def render_form(self):
        #z2.switch_on(self, request_layer=self.request_layer)
        self.form.update(self.form_instance)
        return self.form.render(self.form_instance)
        #return self.form_instance()

    # view methods

    def can_reply(self):
        return getSecurityManager().checkPermission('Reply to item', aq_inner(self.context))

    def can_manage(self):
        return getSecurityManager().checkPermission('Manage portal', aq_inner(self.context))

    def is_discussion_allowed(self):
        context = aq_inner(self.context)
        conversation = IConversation(context)
        return conversation.enabled

    def get_replies(self, workflow_actions=False):
        context = aq_inner(self.context)
        conversation = IConversation(context)

        def replies_with_workflow_actions():
            # Return dict with workflow actions
            #context = aq_inner(self.context)
            wf = getToolByName(context, 'portal_workflow')

            for r in conversation.getThreads():
                comment_obj = r['comment']
                # list all possible workflow actions
                actions = [a for a in wf.listActionInfos(object=comment_obj)
                               if a['category'] == 'workflow' and a['allowed']]
                r = r.copy()
                r['actions'] = actions
                yield r

        # Return all direct replies
        if conversation.total_comments > 0:
            if workflow_actions:
                return replies_with_workflow_actions()
            else:
                return conversation.getThreads()
        else:
            return None


    def get_commenter_home_url(self, username):
        if username is None:
            return None
        else:
            return "%s/author/%s" % (self.context.portal_url(), username)

    def get_commenter_portrait(self, username):

        if username is None:
            # return the default user image if no username is given
            return 'defaultUser.gif'
        else:
            portal_membership = getToolByName(self.context, 'portal_membership', None)
            return portal_membership.getPersonalPortrait(username).absolute_url();

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
        return self.portal_state.anonymous()

    def login_action(self):
        return '%s/login_form?came_from=%s' % (self.navigation_root_url, url_quote(self.request.get('URL', '')),)

    def format_time(self, time):
        # We have to transform Python datetime into Zope DateTime
        # before we can call toLocalizedTime.
        util = getToolByName(self.context, 'translation_service')
        zope_time = DateTime(time.year, time.month, time.day, time.hour, time.minute, time.second)
        return util.toLocalizedTime(zope_time, long_format=True)

CommentsViewlet = wrap_form(CommentForm, __wrapper_class=ViewletFormWrapper)


class AddComment(BrowserView):
    """Add a comment to a conversation
    """

    def __call__(self):

        if self.request.has_key('form.button.AddComment'):

            context = aq_inner(self.context)

            subject = self.request.get('subject')
            text = self.request.get('body_text')
            author_username = self.request.get('author_username')
            author_email = self.request.get('author_email')

            # Check the form input
            if author_username == '':
                IStatusMessage(self.request).addStatusMessage(\
                    _("Username field is empty."),
                    type="info")
                return self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url())
            if author_email == '':
                IStatusMessage(self.request).addStatusMessage(\
                    _("Email field is empty."),
                    type="info")
                return self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url())
            if subject == '':
                IStatusMessage(self.request).addStatusMessage(\
                    _("Subject field is empty."),
                    type="info")
                return self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url())
            if text == '':
                IStatusMessage(self.request).addStatusMessage(\
                    _("Comment field is empty."),
                    type="info")
                return self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url())

            # The add-comment view is called on the conversation object
            conversation = context

            # Create the comment
            comment = CommentFactory()
            comment.title = subject
            comment.text = text

            portal_membership = getToolByName(context, 'portal_membership')

            if portal_membership.isAnonymousUser():
                comment.creator = author_username
                comment.author_name = author_username
                comment.author_email = author_email
                comment.creation_date = comment.modification_date = datetime.now()
            else:
                member = portal_membership.getAuthenticatedMember()
                fullname = member.getProperty('fullname')
                if fullname == '' or None:
                    comment.creator = member.id
                else:
                    comment.creator = fullname
                comment.author_username = member.getUserName()
                comment.author_name = member.getProperty('fullname')
                comment.author_email = member.getProperty('email')
                comment.creation_date = comment.modification_date = datetime.now()

            # Add comment to the conversation
            comment_id = conversation.addComment(comment)

            # Redirect to comment (inside a content object page)
            #self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url() + '#comment-' + str(comment_id))
            self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url() + '#' + str(comment_id))

class ReplyToComment(BrowserView):
    """Reply to a comment
    """

    def __call__(self):

        context = aq_inner(self.context)

        if self.request.has_key('form.button.AddComment'):

            reply_to_comment_id = self.request.get('form.reply_to_comment_id')

            subject = self.request.get('subject')
            text = self.request.get('body_text')
            author_username = self.request.get('author_username')
            author_email = self.request.get('author_email')

            # Check the form input
            if author_username == '':
                IStatusMessage(self.request).addStatusMessage(\
                    _("Username field is empty."),
                    type="info")
                return self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url())
            if author_email == '':
                IStatusMessage(self.request).addStatusMessage(\
                    _("Email field is empty."),
                    type="info")
                return self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url())
            if subject == '':
                IStatusMessage(self.request).addStatusMessage(\
                    _("Subject field is empty."),
                    type="info")
                return self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url())
            if text == '':
                IStatusMessage(self.request).addStatusMessage(\
                    _("Comment field is empty."),
                    type="info")
                return self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url())

            # The add-comment view is called on the conversation object
            conversation = context

            # Fetch the comment we want to reply to
            comment_to_reply_to = conversation.get(reply_to_comment_id)

            replies = IReplies(comment_to_reply_to)

            # Create the comment
            comment = CommentFactory()
            comment.title = subject
            comment.text = text

            portal_membership = getToolByName(context, 'portal_membership')

            if portal_membership.isAnonymousUser():
                comment.creator = author_username
                comment.author_name = author_username
                comment.author_email = author_email
                comment.creation_date = comment.modification_date = datetime.now()
            else:
                member = portal_membership.getAuthenticatedMember()
                fullname = member.getProperty('fullname')
                if fullname == '' or None:
                    comment.creator = member.id
                else:
                    comment.creator = fullname
                comment.author_username = member.getUserName()
                comment.author_name = member.getProperty('fullname')
                comment.author_email = member.getProperty('email')
                comment.creation_date = comment.modification_date = datetime.now()

            # Add the reply to the comment
            new_re_id = replies.addComment(comment)

            # Redirect to comment (inside a content object page)
            #self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url() + '#comment-' + str(reply_to_comment_id))
            # Todo: Temporarily remove the "#comment-" to fix a bug
            # in CMFPlone/skins/plone_ecmascript/form_tabbing.js
            self.request.response.redirect(aq_parent(aq_inner(context)).absolute_url() + '#' + str(reply_to_comment_id))