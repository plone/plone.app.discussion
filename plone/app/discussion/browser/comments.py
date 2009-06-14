from datetime import datetime

from urllib import quote as url_quote

from zope.interface import implements

from zope.component import createObject, getMultiAdapter, queryUtility

from zope.viewlet.interfaces import IViewlet

from Acquisition import aq_inner, aq_parent, aq_base

from AccessControl import getSecurityManager

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry

from plone.app.layout.viewlets.common import ViewletBase

from plone.app.discussion.interfaces import IConversation, IComment, IReplies, IDiscussionSettings
from plone.app.discussion.conversation import conversationAdapterFactory

from plone.app.discussion.comment import CommentFactory


class View(BrowserView):
    """Comment View
    """

    def __call__(self):
        # Redirect from /path/to/object/++conversation++default/123456789
        # to /path/to/object#comment-123456789
        comment_id = aq_parent(self).id
        self.request.response.redirect(aq_parent(aq_parent(aq_parent(self))).absolute_url() + '#comment-' + comment_id)

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
        conversation = conversationAdapterFactory(self.context)
        return conversation.enabled

    def get_replies(self, workflow_actions=False):

        # Acquisition wrap the conversation
        context = aq_inner(self.context)
        conversation = IConversation(context)
        conversation = IConversation(context).__of__(context)

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
        # Todo: return localized time
        return time.strftime("%a, %d %b %Y %H:%M")
        # XXX: Not working, returns None !!!
        #return self.context.restrictedTraverse('@@plone').toLocalizedTime(time, long_format=True)

class AddComment(BrowserView):
    """Add a comment to a conversation
    """

    def __call__(self):

        if self.request.has_key('form.button.AddComment'):

            subject = self.request.get('subject')
            text = self.request.get('body_text')
            author_username = self.request.get('author_username')
            author_email = self.request.get('author_email')

            # The add-comment view is called on the conversation object
            conversation = self.context

            # Create the comment
            comment = CommentFactory()
            comment.title = subject
            comment.text = text

            portal_membership = getToolByName(self.context, 'portal_membership')

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
            self.request.response.redirect(aq_parent(aq_inner(self.context)).absolute_url() + '#comment-' + str(comment_id))

class ReplyToComment(BrowserView):
    """Reply to a comment
    """

    def __call__(self):

        if self.request.has_key('form.button.AddComment'):

            reply_to_comment_id = self.request.get('form.reply_to_comment_id')
            subject = self.request.get('subject')
            text = self.request.get('body_text')

            # The add-comment view is called on the conversation object
            conversation = self.context

            # Fetch the comment we want to reply to
            comment_to_reply_to = conversation.get(reply_to_comment_id)

            replies = IReplies(comment_to_reply_to)

            # Create the comment
            comment = CommentFactory()
            comment.title = subject
            comment.text = text

            # Add the reply to the comment
            new_re_id = replies.addComment(comment)

            # Redirect to comment (inside a content object page)
            self.request.response.redirect(aq_parent(aq_inner(self.context)).absolute_url() + '#comment-' + str(reply_to_comment_id))

class DeleteComment(BrowserView):
    """Delete a comment from a conversation
    """

    def __call__(self):

        comment = aq_inner(self.context)
        comment_id = self.context.id

        conversation = self.context.__parent__

        del conversation[comment_id]

        self.context.plone_utils.addPortalMessage('Comment %s deleted' % comment_id)
        return self.context.REQUEST.RESPONSE.redirect(self.context.REQUEST.HTTP_REFERER)

class PublishComment(BrowserView):
    """Publish a comment
    """

    def __call__(self):

        comment = aq_inner(self.context)
        comment_id = self.context.id

        workflow_action = self.request.form['workflow_action']
        portal_workflow = getToolByName(comment, 'portal_workflow')
        portal_workflow.doActionFor(comment, workflow_action)

        self.context.plone_utils.addPortalMessage('Workflow action for commment %s changed (%s)' % (comment_id, workflow_action))
        return self.context.REQUEST.RESPONSE.redirect(self.context.REQUEST.HTTP_REFERER)
