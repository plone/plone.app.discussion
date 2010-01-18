from Acquisition import aq_parent

from Products.Five.browser import BrowserView

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