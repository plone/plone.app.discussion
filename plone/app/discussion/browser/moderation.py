# coding: utf-8
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone import api
from plone.app.discussion.events import CommentPublishedEvent
from plone.app.discussion.events import CommentTransitionEvent
from plone.app.discussion.events import CommentDeletedEvent
from plone.app.discussion.interfaces import _
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IReplies
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.event import notify


# Translations for generated values in buttons
# States
_('comment_pending', default='pending')
# _('comment_approved', default='published')
_('comment_published', default='published')
_('comment_rejected', default='rejected')
_('comment_spam', default='marked as spam')
# Transitions
_('Recall')
_('Approve')
_('Reject')
_('Spam')
PMF = _


class TranslationHelper(BrowserView):

    def translate(self, text=""):
        return _(text)

    def translate_comment_review_state(self, rs):
        # use PMF instead of _ here so i18ndude doesn't extract "comment_"
        return PMF("comment_" + rs, default=rs)


class View(BrowserView):
    """Show comment moderation view."""

    template = ViewPageTemplateFile('moderation.pt')
    try:
        template.id = '@@moderate-comments'
    except AttributeError:
        # id is not writeable in Zope 2.12
        pass

    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self.workflowTool = getToolByName(self.context, 'portal_workflow')
        self.transitions = []

    def __call__(self):
        self.request.set('disable_border', True)
        self.request.set('review_state',
                         self.request.get('review_state', 'pending'))
        return self.template()

    def comments(self):
        """Return comments of defined review_state.

        review_state is string or list of strings.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        if self.request.review_state == 'all':
            return catalog(object_provides=IComment.__identifier__,
                           sort_on='created',
                           sort_order='reverse')
        return catalog(object_provides=IComment.__identifier__,
                       review_state=self.request.review_state,
                       sort_on='created',
                       sort_order='reverse')

    def moderation_enabled(self):
        """Return true if a review workflow is enabled on 'Discussion Item'
        content type.

        A 'review workflow' is characterized by implementing a 'pending'
        workflow state.
        """
        workflows = self.workflowTool.getChainForPortalType(
            'Discussion Item')
        if workflows:
            comment_workflow = self.workflowTool[workflows[0]]
            if 'pending' in comment_workflow.states:
                return True
        return False

    @property
    def moderation_multiple_state_enabled(self):
        """Return true if a 'review multiple state workflow' is enabled on
        'Discussion Item' content type.

        A 'review multipe state workflow' is characterized by implementing
        a 'rejected' workflow state and a 'spam' workflow state.
        """
        workflows = self.workflowTool.getChainForPortalType(
            'Discussion Item')
        if workflows:
            comment_workflow = self.workflowTool[workflows[0]]
            if 'spam' in comment_workflow.states:
                return True
        return False

    def allowed_transitions(self, obj=None):
        """Return allowed workflow transitions for obj.

        Example: pending

        [{'id': 'mark_as_spam', 'url': 'http://localhost:8083/PloneRejected/testfolder/testpage/++conversation++default/1575415863542780/content_status_modify?workflow_action=mark_as_spam', 'icon': '', 'category': 'workflow', 'transition': <TransitionDefinition at /PloneRejected/portal_workflow/comment_review_workflow/transitions/mark_as_spam>, 'title': 'Spam', 'link_target': None, 'visible': True, 'available': True, 'allowed': True},
        {'id': 'publish',
            'url': 'http://localhost:8083/PloneRejected/testfolder/testpage/++conversation++default/1575415863542780/content_status_modify?workflow_action=publish',
            'icon': '',
            'category': 'workflow',
            'transition': <TransitionDefinition at /PloneRejected/portal_workflow/comment_review_workflow/transitions/publish>,
            'title': 'Approve',
            'link_target': None, 'visible': True, 'available': True, 'allowed': True},
        {'id': 'reject', 'url': 'http://localhost:8083/PloneRejected/testfolder/testpage/++conversation++default/1575415863542780/content_status_modify?workflow_action=reject', 'icon': '', 'category': 'workflow', 'transition': <TransitionDefinition at /PloneRejected/portal_workflow/comment_review_workflow/transitions/reject>, 'title': 'Reject', 'link_target': None, 'visible': True, 'available': True, 'allowed': True}]
        """
        if obj:
            transitions = [
                a for a in self.workflowTool.listActionInfos(object=obj)
                if a['category'] == 'workflow' and a['allowed']
                ]
            return transitions


class ModerateCommentsEnabled(BrowserView):

    def __call__(self):
        """Returns true if a 'review workflow' is enabled on 'Discussion Item'
           content type. A 'review workflow' is characterized by implementing
           a 'pending' workflow state.
        """
        context = aq_inner(self.context)
        workflowTool = getToolByName(context, 'portal_workflow', None)
        comment_workflow = workflowTool.getChainForPortalType(
            'Discussion Item')
        if comment_workflow:
            comment_workflow = comment_workflow[0]
            comment_workflow = workflowTool[comment_workflow]
            if 'pending' in comment_workflow.states:
                return True

        return False


class DeleteComment(BrowserView):
    """Delete a comment from a conversation.

       This view is always called directly on the comment object:

         http://nohost/front-page/++conversation++default/1286289644723317/\
         @@moderate-delete-comment

       Each table row (comment) in the moderation view contains a hidden input
       field with the absolute URL of the content object:

         <input type="hidden"
                value="http://nohost/front-page/++conversation++default/\
                       1286289644723317"
                name="selected_obj_paths:list">

       This absolute URL is called from a jQuery method that is bind to the
       'delete' button of the table row. See javascripts/moderation.js for more
       details.
    """

    def __call__(self):
        comment = aq_inner(self.context)
        conversation = aq_parent(comment)
        content_object = aq_parent(conversation)
        # conditional security
        # base ZCML condition zope2.deleteObject allows 'delete own object'
        # modify this for 'delete_own_comment_allowed' controlpanel setting
        if self.can_delete(comment):
            del conversation[comment.id]
            content_object.reindexObject()
            notify(CommentDeletedEvent(self.context, comment))
            IStatusMessage(self.context.REQUEST).addStatusMessage(
                _('Comment deleted.'),
                type='info')
        came_from = self.context.REQUEST.HTTP_REFERER
        # if the referrer already has a came_from in it, don't redirect back
        if (len(came_from) == 0 or 'came_from=' in came_from or
                not getToolByName(
                content_object, 'portal_url').isURLInPortal(came_from)):
            came_from = content_object.absolute_url()
        return self.context.REQUEST.RESPONSE.redirect(came_from)

    def can_delete(self, reply):
        """Returns true if current user has the 'Delete comments'
        permission.
        """
        return getSecurityManager().checkPermission('Delete comments',
                                                    aq_inner(reply))


class DeleteOwnComment(DeleteComment):
    """Delete an own comment if it has no replies.

    Following conditions have to be true for a user to be able to delete his
    comments:
    * "Delete own comments" permission
    * no replies to the comment
    * Owner role directly assigned on the comment object
    """

    def could_delete(self, comment=None):
        """Returns true if the comment could be deleted if it had no replies.
        """
        sm = getSecurityManager()
        comment = comment or aq_inner(self.context)
        userid = sm.getUser().getId()
        return (
            sm.checkPermission('Delete own comments', comment) and
            'Owner' in comment.get_local_roles_for_userid(userid)
        )

    def can_delete(self, comment=None):
        comment = comment or self.context
        return (
            len(IReplies(aq_inner(comment))) == 0 and
            self.could_delete(comment=comment)
        )

    def __call__(self):
        if self.can_delete():
            super(DeleteOwnComment, self).__call__()
        else:
            raise Unauthorized("You're not allowed to delete this comment.")


class CommentTransition(BrowserView):
    r"""Publish, reject, recall a comment or mark it as spam.

    This view is always called directly on the comment object:

        http://nohost/front-page/++conversation++default/1286289644723317/\
        @@transmit-comment

    Each table row (comment) in the moderation view contains a hidden input
    field with the absolute URL of the content object:

        <input type="hidden"
            value="http://nohost/front-page/++conversation++default/\
                1286289644723317"
            name="selected_obj_paths:list">

    This absolute URL is called from a jQuery method that is bind to the
    'delete' button of the table row. See javascripts/moderation.js for more
    details.
    """

    def __call__(self):
        """Call CommentTransition."""
        comment = aq_inner(self.context)
        content_object = aq_parent(aq_parent(comment))
        workflow_action = self.request.form.get('workflow_action', 'publish')
        api.content.transition(comment, transition=workflow_action)
        comment.reindexObject()
        content_object.reindexObject(idxs=['total_comments'])
        notify(CommentPublishedEvent(self.context, comment))
        # for complexer workflows:
        notify(CommentTransitionEvent(self.context, comment))
        review_state_new = api.content.get_state(comment, '')

        comment_state_translated = self.context.restrictedTraverse("translationhelper").translate_comment_review_state(review_state_new)

        msgid = _(
            "comment_transmitted",
            default='Comment ${comment_state_translated}.',
            mapping={"comment_state_translated": comment_state_translated})
        translated = self.context.translate(msgid)
        api.portal.show_message(translated, self.context.REQUEST)

        came_from = self.context.REQUEST.HTTP_REFERER
        # if the referrer already has a came_from in it, don't redirect back
        if (len(came_from) == 0
            or 'came_from=' in came_from
            or not getToolByName(
                content_object, 'portal_url').isURLInPortal(came_from)):
            came_from = content_object.absolute_url()
        return self.context.REQUEST.RESPONSE.redirect(came_from)


class BulkActionsView(BrowserView):
    """Call bulk action: publish/approve, delete (, reject, recall, mark as spam).

       Each table row of the moderation view has a checkbox with the absolute
       path (without host and port) of the comment objects:

         <input type="checkbox"
                name="paths:list"
                value="/plone/front-page/++conversation++default/\
                       1286289644723317"
                id="cb_1286289644723317" />

       If checked, the comment path will occur in the 'paths' variable of
       the request when the bulk actions view is called. The bulk action
       (delete, publish, etc.) will be applied to all comments that are
       included.

       The paths have to be 'traversable':

         /plone/front-page/++conversation++default/1286289644723317

    """

    def __init__(self, context, request):
        super(BulkActionsView, self).__init__(context, request)
        self.workflowTool = getToolByName(context, 'portal_workflow')

    def __call__(self):
        """Call BulkActionsView."""
        if 'form.select.BulkAction' in self.request:
            bulkaction = self.request.get('form.select.BulkAction')
            self.paths = self.request.get('paths')
            if self.paths:
                if bulkaction == '-1':
                    # no bulk action was selected
                    pass
                elif bulkaction == 'delete':
                    self.delete()
                else:
                    self.transmit(bulkaction)

    def transmit(self, action=None):
        """Transmit all comments in the paths variable to requested review_state.

        Expects a list of absolute paths (without host and port):

        /Plone/startseite/++conversation++default/1286200010610352
        """
        context = aq_inner(self.context)
        for path in self.paths:
            comment = context.restrictedTraverse(path)
            content_object = aq_parent(aq_parent(comment))
            allowed_transitions = [
                transition['id'] for transition in self.workflowTool.listActionInfos(object=comment)
                if transition['category'] == 'workflow' and transition['allowed']
                ]
            if action in allowed_transitions:
                self.workflowTool.doActionFor(comment, action)
                comment.reindexObject()
                content_object.reindexObject(idxs=['total_comments'])
                notify(CommentPublishedEvent(content_object, comment))
                # for complexer workflows:
                notify(CommentTransitionEvent(self.context, comment))

    def delete(self):
        """Delete all comments in the paths variable.

        Expects a list of absolute paths (without host and port):

        /Plone/startseite/++conversation++default/1286200010610352
        """
        context = aq_inner(self.context)
        for path in self.paths:
            comment = context.restrictedTraverse(path)
            conversation = aq_parent(comment)
            content_object = aq_parent(conversation)
            del conversation[comment.id]
            content_object.reindexObject(idxs=['total_comments'])
            notify(CommentDeletedEvent(content_object, comment))
