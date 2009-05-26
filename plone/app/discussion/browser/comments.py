from datetime import datetime

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewlet

from Acquisition import aq_inner, aq_parent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.discussion.interfaces import IComment

from plone.app.discussion.conversation import conversationAdapterFactory

from plone.app.discussion.comment import CommentFactory

from zope.component import createObject

class CommentsViewlet(BrowserView):
    """Discussion Viewlet
    """

    implements(IViewlet)

    template = ViewPageTemplateFile('comments.pt')

    def __init__(self, context, request, view, manager):
        super(CommentsViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.view = view
        self.manager = manager
        self.portal_state = getMultiAdapter((context, self.request), name=u"plone_portal_state")

    def update(self):
        pass

    def replies(self):
        conversation = conversationAdapterFactory(self.context)
        return conversation.items()

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

            # Add comment to the conversation
            conversation.addComment(comment)

            # TODO: Redirect to the document object page
            self.request.response.redirect(aq_parent(aq_inner(self.context)).absolute_url())
