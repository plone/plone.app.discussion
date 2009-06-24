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



class View(BrowserView):
    """Comment View
    """

    def __call__(self):
        # Redirect from /path/to/object/++conversation++default/123456789
        # to /path/to/object#comment-123456789
        comment_id = aq_parent(self).id
        #self.request.response.redirect(aq_parent(aq_parent(aq_parent(self))).absolute_url() + '#comment-' + comment_id)
        self.request.response.redirect(aq_parent(aq_parent(aq_parent(self))).absolute_url() + '#' + comment_id)

class CommentsViewlet(ViewletBase):
    """Discussion Viewlet
    """

    implements(IViewlet)

    template = ViewPageTemplateFile('comments.pt')

    def update(self):
        super(CommentsViewlet, self).update()
        self.portal_discussion = getToolByName(self.context, 'portal_discussion', None)
        self.portal_membership = getToolByName(self.context, 'portal_membership', None)

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
        settings = registry.for_interface(IDiscussionSettings)
        return settings.anonymous_comments

    def show_commenter_image(self):
        # Check if showing commenter image is enabled in the registry
        registry = queryUtility(IRegistry)
        settings = registry.for_interface(IDiscussionSettings)
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

class DeleteComment(BrowserView):
    """Delete a comment from a conversation
    """

    def __call__(self):

        context = aq_inner(self.context)
        comment_id = self.context.id

        conversation = aq_parent(context)

        del conversation[comment_id]

        # Todo: i18n
        IStatusMessage(self.request).addStatusMessage(
            _('Comment %s deleted' % comment_id),
            type="info")
        return context.REQUEST.RESPONSE.redirect(context.REQUEST.HTTP_REFERER)

class PublishComment(BrowserView):
    """Publish a comment
    """

    def __call__(self):

        comment = aq_inner(self.context)
        comment_id = self.context.id

        workflow_action = self.request.form['workflow_action']
        portal_workflow = getToolByName(comment, 'portal_workflow')
        portal_workflow.doActionFor(comment, workflow_action)

        # Todo: i18n
        IStatusMessage(self.request).addStatusMessage(
            _('Workflow action for commment %s changed (%s)' % (comment_id, workflow_action)),
            type="info")
        return self.context.REQUEST.RESPONSE.redirect(self.context.REQUEST.HTTP_REFERER)
