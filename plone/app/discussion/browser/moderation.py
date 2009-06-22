from Acquisition import aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

class View(BrowserView):
    """
    """

    template = ViewPageTemplateFile('moderation.pt')

    def __call__(self):
        return self.template()

    def cook(self, text):
        return text

    def comments_pending_review(self):

        self.state = self.request.get('review_state', 'pending')
        self.transition = self.request.get('publish_transition', 'pending')
        self.limit = self.request.get('limit', 100)

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')

        return catalog(
                path='/'.join(context.getPhysicalPath()),
                portal_type='Discussion Item',
                review_state=self.state,
                sort_on='created',
                sort_limit=self.limit,
            )