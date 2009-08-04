from Acquisition import aq_inner, aq_parent, aq_base

from AccessControl import getSecurityManager

from datetime import datetime
from DateTime import DateTime

from urllib import quote as url_quote

from zope import interface, schema

from zope.annotation import IAttributeAnnotatable

from zope.component import createObject, getMultiAdapter, queryUtility

from zope.interface import Interface, implements

from zope.viewlet.interfaces import IViewlet

from z3c.form import form, field, button, interfaces

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

from plone.registry.interfaces import IRegistry

from plone.app.layout.viewlets.common import ViewletBase

from plone.app.discussion.comment import Comment, CommentFactory
from plone.app.discussion.interfaces import IConversation, IComment, IReplies, IDiscussionSettings

from plone.z3cform import layout, z2
from plone.z3cform.fieldsets import extensible

class View(BrowserView):
    """Comment View.

    Redirect from /path/to/object/++conversation++default/123456789
    to /path/to/object#comment-123456789.
    """

    def __call__(self):
        comment_id = aq_parent(self).id
        self.request.response.redirect(
            aq_parent(aq_parent(aq_parent(self))).absolute_url() +
            '#' + str(comment_id))

class CommentForm(extensible.ExtensibleForm, form.Form):

    ignoreContext = True # don't use context to get widget data
    label = _(u"Add a comment")

    @property
    def fields(self):
        portal_membership = getToolByName(self.context, 'portal_membership')
        if portal_membership.isAnonymousUser():
            return field.Fields(IComment).omit('portal_type',
                                               '__parent__',
                                               '__name__',
                                               'comment_id',
                                               'mime_type',
                                               'creator',
                                               'creation_date',
                                               'modification_date',
                                               'author_username',)
        else:
            return field.Fields(IComment).omit('portal_type',
                                               '__parent__',
                                               '__name__',
                                               'comment_id',
                                               'mime_type',
                                               'creator',
                                               'creation_date',
                                               'modification_date',
                                               'author_username',
                                               'author_name',
                                               'author_email',)

    def updateWidgets(self):
        super(CommentForm, self).updateWidgets()
        self.widgets['in_reply_to'].mode = interfaces.HIDDEN_MODE

    @button.buttonAndHandler(_(u"Comment"))
    def handleComment(self, action):
        data, errors = self.extractData()

        if data.has_key('title') and data.has_key('text'):

            title = data['title']
            text = data['text']

            if data.has_key('author_name'):
                author_name = data['author_name']
            else:
                author_name = u""

            if data.has_key('author_username'):
                author_name = data['author_username']
            else:
                author_username = u""

            if data.has_key('author_email'):
                author_email = data['author_email']
            else:
                author_email = u""

            # The add-comment view is called on the conversation object
            conversation = IConversation(self.__parent__)

            # Create the comment
            comment = createObject('plone.Comment')
            comment.title = title
            comment.text = text

            portal_membership = getToolByName(self.context, 'portal_membership')

            if portal_membership.isAnonymousUser():
                comment.creator = author_name
                comment.author_name = author_name
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
            self.request.response.redirect(
                aq_parent(aq_inner(self.context)).absolute_url() +
                '#' + str(comment_id))

    @button.buttonAndHandler(_(u"Reply"))
    def handleReply(self, action):

        data, errors = self.extractData()

        if data.has_key('title') and data.has_key('text') and data.has_key('in_reply_to'):

            title = data['title']
            text = data['text']
            reply_to_comment_id = data['in_reply_to']

            if data.has_key('author_name'):
                author_name = data['author_name']
            else:
                author_name = u""

            if data.has_key('author_username'):
                author_name = data['author_username']
            else:
                author_username = u""

            if data.has_key('author_email'):
                author_email = data['author_email']
            else:
                author_email = u""

            # The add-comment view is called on the conversation object
            conversation = IConversation(self.__parent__)

            # Fetch the comment we want to reply to
            comment_to_reply_to = conversation.get(reply_to_comment_id)

            replies = IReplies(comment_to_reply_to)

            # Create the comment
            comment = createObject('plone.Comment')
            comment.title = title
            comment.text = text

            portal_membership = getToolByName(self.context, 'portal_membership')

            if portal_membership.isAnonymousUser():
                comment.creator = author_name
                comment.author_name = author_name
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
            self.request.response.redirect(aq_parent(aq_inner(self.context)).absolute_url() + '#' + str(reply_to_comment_id))

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        # This method should never be called, it's only there to show
        # a cancel button that is handled by a jQuery method.
        pass

class CommentsViewlet(ViewletBase, layout.FormWrapper):

    form = CommentForm

    def index(self):
        return ViewPageTemplateFile('comments.pt').__of__(self)(self)

    def __init__(self, context, request, view, manager):
        super(CommentsViewlet, self).__init__(context, request, view, manager)
        if self.form is not None:
            self.form_instance = self.form(self.context.aq_inner, self.request)
            self.form_instance.__name__ = self.__name__

        self.portal_discussion = getToolByName(self.context, 'portal_discussion', None)
        self.portal_membership = getToolByName(self.context, 'portal_membership', None)

    def render_form(self):
        z2.switch_on(self, request_layer=self.request_layer)
        self.form.update(self.form_instance)
        return self.form.render(self.form_instance)

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