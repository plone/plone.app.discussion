from datetime import datetime

from urllib import quote as url_quote

from zope.interface import implements

from zope.component import createObject
from zope.component import getMultiAdapter

from zope.viewlet.interfaces import IViewlet

from Acquisition import aq_inner, aq_parent

from AccessControl import getSecurityManager

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from plone.app.layout.viewlets.common import ViewletBase

from plone.app.discussion.interfaces import IComment, IReplies
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

    def is_discussion_allowed(self):
        if self.portal_discussion is None:
            return False
        else:
            return self.portal_discussion.isDiscussionAllowedFor(aq_inner(self.context))

    def get_replies(self):
        # Return all direct replies
        conversation = conversationAdapterFactory(self.context)

        if conversation.total_comments > 0:
            return conversation.getThreads()
        else:
            return False

    def is_anonymous(self):
        return self.portal_state.anonymous()

    def login_action(self):
        return '%s/login_form?came_from=%s' % (self.navigation_root_url, url_quote(self.request.get('URL', '')),)

    def format_time(self, time):
        # TODO: to localized time not working!!!
        #util = getToolByName(self.context, 'translation_service')
        #return util.ulocalized_time(time, 1, self.context, domain='plonelocales')
        return time

class AddComment(BrowserView):
    """Add a comment to a conversation
    """

    def __call__(self):

        if self.request.has_key('form.button.AddComment'):

            subject = self.request.get('subject')
            text = self.request.get('body_text')

            # The add-comment view is called on the conversation object
            conversation = self.context

            # Create the comment
            comment = CommentFactory()
            comment.title = subject
            comment.text = text

            portal_membership = getToolByName(self.context, 'portal_membership')

            if portal_membership.isAnonymousUser():
                # TODO: Not implemented yet
                pass
            else:
                member = portal_membership.getAuthenticatedMember()
                comment.creator = member.getProperty('fullname')
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
            self.request.response.redirect(aq_parent(aq_inner(self.context)).absolute_url() + '#comment-' + str(comment_id))
