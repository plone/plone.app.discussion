# -*- coding: utf-8 -*-
from Acquisition import aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from Products.statusmessages.interfaces import IStatusMessage

from plone.app.discussion.interfaces import _
from plone.app.discussion.interfaces import IComment


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
        del conversation[comment.id]
        IStatusMessage(self.context.REQUEST).addStatusMessage(
            _("Comment deleted."),
            type="info")
        came_from = self.context.REQUEST.HTTP_REFERER
        if len(came_from) == 0:
            came_from = content_object.absolute_url()
        return self.context.REQUEST.RESPONSE.redirect(came_from)


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
        current_state = workflowTool.getInfoFor(comment, 'review_state')
        if current_state != 'published':
            workflowTool.doActionFor(comment, 'publish')
        catalogTool = getToolByName(comment, 'portal_catalog')
        catalogTool.reindexObject(comment)
        IStatusMessage(self.context.REQUEST).addStatusMessage(
            _("Comment approved."),
            type="info")
        came_from = self.context.REQUEST.HTTP_REFERER
        if len(came_from) == 0:
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
            workflowTool = getToolByName(comment, 'portal_workflow')
            current_state = workflowTool.getInfoFor(comment, 'review_state')
            if current_state != 'published':
                workflowTool.doActionFor(comment, 'publish')
            catalog = getToolByName(comment, 'portal_catalog')
            catalog.reindexObject(comment)

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
            del conversation[comment.id]
