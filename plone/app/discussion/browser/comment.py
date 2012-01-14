from Acquisition import aq_inner, aq_parent

from Products.Five.browser import BrowserView


class View(BrowserView):
    """Comment View.

    When the view of a comment object is called directly, redirect to the
    the page (content object) and the location (HTML-anchor) where the comment
    has been posted.

    Redirect from the comment object URL
    "/path/to/object/++conversation++default/123456789" to the content object
    where the comment has been posted appended by an HTML anchor that points to
    the comment "/path/to/object#comment-123456789".

    Context is the comment object. The parent of the comment object is the
    conversation. The parent of the conversation is the content object where
    the comment has been posted.
    """

    def __call__(self):
        context = aq_inner(self.context)
        self.request.response.redirect(
            aq_parent(aq_parent(context)).absolute_url() +
            '#' + str(context.id)
            )
