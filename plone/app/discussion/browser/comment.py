from Acquisition import aq_inner, aq_parent
from AccessControl import getSecurityManager

from zope.component import getMultiAdapter
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from plone.app.discussion import PloneAppDiscussionMessageFactory as _
from comments import CommentForm
from z3c.form import button
from plone.z3cform.layout import wrap_form


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
        ptool = getToolByName(context, 'portal_properties')
        view_action_types = ptool.site_properties.typesUseViewActionInListings
        obj = aq_parent(aq_parent(context))
        url = obj.absolute_url()

        """
        Image and File types, as well as many other customized archetypes
        require /view be appended to the url to see the comments, otherwise it
        will redirect right to the binary object, bypassing comments.
        """
        if obj.portal_type in view_action_types:
            url = "%s/view" % url

        self.request.response.redirect('%s#%s' % (url, context.id))


class EditCommentForm(CommentForm):
    """Form to edit an existing comment."""
    ignoreContext = True
    id = "edit-comment-form"
    label = _(u'edit_comment_form_title', default=u'Edit comment')

    def updateWidgets(self):
        super(EditCommentForm, self).updateWidgets()
        self.widgets['text'].value = self.context.text
        # We have to rename the id, otherwise TinyMCE can't initialize
        # because there are two textareas with the same id.
        self.widgets['text'].id = 'overlay-comment-text'

    def _redirect(self, target=''):
        if not target:
            portal_state = getMultiAdapter((self.context, self.request),
                                           name=u'plone_portal_state')
            target = portal_state.portal_url()
        self.request.response.redirect(target)

    @button.buttonAndHandler(_(u"edit_comment_form_button",
                             default=u"Edit comment"), name='comment')
    def handleComment(self, action):

        # Validate form
        data, errors = self.extractData()
        if errors:
            return

        # Check permissions
        can_edit = getSecurityManager().checkPermission(
            'Edit comments',
            self.context)
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.isAnonymousUser() or not can_edit:
            return

        # Update text
        self.context.text = data['text']

        # Redirect to comment
        IStatusMessage(self.request).add(_(u'comment_edit_notification',
                                           default="Comment was edited"),
                                         type='info')
        return self._redirect(
            target=self.action.replace("@@edit-comment", "@@view"))

    @button.buttonAndHandler(_(u'cancel_form_button',
                               default=u'Cancel'), name='cancel')
    def handle_cancel(self, action):
            IStatusMessage(self.request).add(
                _(u'comment_edit_cancel_notification',
                  default=u'Edit comment cancelled'),
                type='info')
            return self._redirect(target=self.context.absolute_url())

EditComment = wrap_form(EditCommentForm)

#EOF
