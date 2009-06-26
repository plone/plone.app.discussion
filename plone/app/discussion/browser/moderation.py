from Acquisition import aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

class View(BrowserView):
    """
    """

    template = ViewPageTemplateFile('moderation.pt')

    def __call__(self):

        context = aq_inner(self.context)

        if self.request.has_key('form.button.FilterPending'):
            self.comments = self.comments_pending()
        elif self.request.has_key('form.button.FilterPublished'):
            self.comments = self.comments_published()
        else:
            self.comments = self.comments_all()
        return self.template()

    def cook(self, text):
        return text

    def comments_workflow_enabled(self):
        return True

    def comments_all(self, start=0, size=None):

        self.state = self.request.get('review_state', 'pending')
        self.transition = self.request.get('publish_transition', 'pending')
        self.limit = self.request.get('limit', 100)

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')

        return catalog(
                portal_type='Discussion Item',
                sort_on='created',
                sort_limit=self.limit,
            )

    def comments_pending(self, start=0, size=None):
        self.state = self.request.get('review_state', 'pending')
        self.transition = self.request.get('publish_transition', 'publish')
        self.limit = self.request.get('limit', 100)

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')

        return catalog(
                portal_type='Discussion Item',
                review_state=self.state,
                sort_on='created',
                sort_limit=self.limit,
            )

    def comments_published(self, start=0, size=None):

        self.state = self.request.get('review_state', 'pending')
        self.transition = self.request.get('publish_transition', 'pending')
        self.limit = self.request.get('limit', 100)

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')

        return catalog(
                portal_type='Discussion Item',
                review_state='published',
                sort_on='created',
                sort_limit=self.limit,
            )

    def comments_spam(self, start=0, size=None):
        return None

class DeleteComment(BrowserView):
    """Delete a comment from a conversation
    """

    def __call__(self):

        context = aq_inner(self.context)
        comment_id = self.context.id

        conversation = aq_parent(context)

        del conversation[comment_id]

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

        catalog = getToolByName(comment, 'portal_catalog')
        catalog.reindexObject(comment)
        comment.reindexObjectSecurity()

        return self.context.REQUEST.RESPONSE.redirect(self.context.REQUEST.HTTP_REFERER)

class BulkActionsView(BrowserView):
    """Bulk actions (unapprove, approve, delete, mark as spam).
    """

    def __call__(self):

        context = aq_inner(self.context)

        if self.request.has_key('form.button.BulkAction'):

            bulkaction = self.request.get('form.bulkaction')
            return bulkaction
