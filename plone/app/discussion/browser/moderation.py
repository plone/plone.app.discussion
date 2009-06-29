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

        if self.request.has_key('form.button.Filter'):
            self.filter = self.request.get('form.button.Filter')
            if self.filter == 'pending':
                self.comments = self.comments_pending()
            elif self.filter == "published":
                self.comments = self.comments_published()
            else:
                raise ValueError('Value %s for filter is not know.' % self.filter)
        else:
            self.comments = self.comments_all()
        return self.template()

    def cook(self, text):
        return text

    def comments_workflow_enabled(self):
        return True

    def comments_all(self, start=0, size=None):

        self.state = self.request.get('review_state', 'pending')
        self.transition = self.request.get('publish_transition', 'publish')
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

class BulkActionsView(BrowserView):
    """Bulk actions (unapprove, approve, delete, mark as spam).
    """

    def __call__(self):

        context = aq_inner(self.context)

        if self.request.has_key('form.button.BulkAction'):

            bulkaction = self.request.get('form.select.BulkAction')

            paths = self.request.get('paths')

            if bulkaction == '-1':
                return self.context.REQUEST.RESPONSE.redirect(self.context.REQUEST.HTTP_REFERER)
            elif bulkaction == 'retract':
                self.retract(paths)
            elif bulkaction == 'publish':
                self.publish(paths)
            elif bulkaction == 'mark_as_spam':
                self.mark_as_spam(paths)
            elif bulkaction == 'delete':
                self.delete(paths)
            else:
                raise KeyError

        return self.context.REQUEST.RESPONSE.redirect(self.context.REQUEST.HTTP_REFERER)

    def retract(self, paths):
        raise NotImplementedError

    def publish(self, paths):
        context = aq_inner(self.context)
        for path in paths:
            comment = context.restrictedTraverse(path)
            portal_workflow = getToolByName(comment, 'portal_workflow')
            portal_workflow.doActionFor(comment, 'publish')
            catalog = getToolByName(comment, 'portal_catalog')
            catalog.reindexObject(comment)

    def mark_as_spam(self, paths):
        raise NotImplementedError

    def delete(self, paths):
        context = aq_inner(self.context)
        for path in paths:
            comment = context.restrictedTraverse(path)
            conversation = aq_parent(comment)
            del conversation[comment.id]
