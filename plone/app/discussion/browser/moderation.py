# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.discussion.interfaces import _
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IReplies
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage


class View(BrowserView):
    """Comment moderation view.
    """
    template = ViewPageTemplateFile('moderation.pt')
    try:
        template.id = '@@moderate-comments'
    except AttributeError:
        # id is not writeable in Zope 2.12
        pass

    def __call__(self):
        self.request.set('disable_border', True)
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        self.comments = catalog(object_provides=IComment.__identifier__,
                                review_state='pending',
                                sort_on='created',
                                sort_order='reverse')
        return self.template()

    def moderation_enabled(self):
        """Returns true if a 'review workflow' is enabled on 'Discussion Item'
           content type. A 'review workflow' is characterized by implementing
           a 'pending' workflow state.
        """
        context = aq_inner(self.context)
        workflowTool = getToolByName(context, 'portal_workflow')
        comment_workflow = workflowTool.getChainForPortalType(
            'Discussion Item')
        if comment_workflow:
            comment_workflow = comment_workflow[0]
            comment_workflow = workflowTool[comment_workflow]
            if 'pending' in comment_workflow.states:
                return True
        return False


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


class PublishComment(BrowserView):
    """Publish a comment.

       This view is always called directly on the comment object:

           http://nohost/front-page/++conversation++default/1286289644723317/\
           @@moderate-publish-comment

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
        content_object = aq_parent(aq_parent(comment))
        workflowTool = getToolByName(comment, 'portal_workflow', None)
        workflow_action = self.request.form.get('workflow_action', 'publish')
        workflowTool.doActionFor(comment, workflow_action)
        comment.reindexObject()
        content_object.reindexObject(idxs=['total_comments'])
        IStatusMessage(self.context.REQUEST).addStatusMessage(
            _('Comment approved.'),
            type='info')
        came_from = self.context.REQUEST.HTTP_REFERER
        # if the referrer already has a came_from in it, don't redirect back
        if (len(came_from) == 0 or 'came_from=' in came_from or
                not getToolByName(
                content_object, 'portal_url').isURLInPortal(came_from)):
            came_from = content_object.absolute_url()
        return self.context.REQUEST.RESPONSE.redirect(came_from)


class BulkActionsView(BrowserView):
    """Bulk actions (unapprove, approve, delete, mark as spam).

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

    def __call__(self):
        if 'form.select.BulkAction' in self.request:
            bulkaction = self.request.get('form.select.BulkAction')
            self.paths = self.request.get('paths')
            if self.paths:
                if bulkaction == '-1':
                    # no bulk action was selected
                    pass
                elif bulkaction == 'retract':
                    self.retract()
                elif bulkaction == 'publish':
                    self.publish()
                elif bulkaction == 'mark_as_spam':
                    self.mark_as_spam()
                elif bulkaction == 'delete':
                    self.delete()
                else:
                    raise KeyError  # pragma: no cover

    def retract(self):
        raise NotImplementedError

    def publish(self):
        """Publishes all comments in the paths variable.

           Expects a list of absolute paths (without host and port):

             /Plone/startseite/++conversation++default/1286200010610352

        """
        context = aq_inner(self.context)
        for path in self.paths:
            comment = context.restrictedTraverse(path)
            content_object = aq_parent(aq_parent(comment))
            workflowTool = getToolByName(comment, 'portal_workflow')
            current_state = workflowTool.getInfoFor(comment, 'review_state')
            if current_state != 'published':
                workflowTool.doActionFor(comment, 'publish')
            comment.reindexObject()
            content_object.reindexObject(idxs=['total_comments'])

    def mark_as_spam(self):
        raise NotImplementedError

    def delete(self):
        """Deletes all comments in the paths variable.

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
