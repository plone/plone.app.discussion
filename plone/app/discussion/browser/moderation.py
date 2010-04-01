from Acquisition import aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.CMFCore.utils import getToolByName

from Products.statusmessages.interfaces import IStatusMessage

from plone.app.discussion.interfaces import _
from plone.app.discussion.interfaces import IComment

# Begin ugly hack. It works around a ContentProviderLookupError: plone.htmlhead error caused by Zope 2 permissions.
# This error occured on Plone 3.3.x only!
#
# Source: http://athenageek.wordpress.com/2008/01/08/contentproviderlookuperror-plonehtmlhead/
# Bug report: https://bugs.launchpad.net/zope2/+bug/176566
#

def _getContext(self):
    self = self.aq_parent
    while getattr(self, '_is_wrapperish', None):
        self = self.aq_parent
    return self    
            
ZopeTwoPageTemplateFile._getContext = _getContext
# End ugly hack.


class View(BrowserView):
    """Moderation View
    """

    template = ViewPageTemplateFile('moderation.pt')
    try:
        template.id = '@@moderate-comments'
    except AttributeError:
        # id is not writeable in Zope 2.12
        pass

    def __call__(self):
        # Hide the editable-object border
        self.request.set('disable_border', True)

        context = aq_inner(self.context)
        
        # Help for path mangling
        portal_url = getToolByName(context, 'portal_url')
        self.portal_url = portal_url()
        self.portal_path = portal_url.getPortalPath()

        catalog = getToolByName(context, 'portal_catalog')

        self.comments = catalog(object_provides=IComment.__identifier__,
                                review_state='pending',
                                sort_on='created',
                                sort_order='reverse')
        return self.template()

    def cook(self, text):
        return text

    def moderation_enabled(self):
        """Returns true if comment moderation workflow is
           enabled on 'Discussion Item' content type.
        """
        context = aq_inner(self.context)
        wf_tool = getToolByName(context, 'portal_workflow')
        if wf_tool.getChainForPortalType('Discussion Item') \
            == ('comment_review_workflow',):
            return True
        else:
            return False
        
    def item_path(self, item):
        # Path mangling to support virtual hosting
        path = item.getPath()[len(self.portal_path):]
        return self.portal_url + path


class DeleteComment(BrowserView):
    """Delete a comment from a conversation
    """

    def __call__(self):

        context = aq_inner(self.context)
        comment_id = self.context.id

        conversation = aq_parent(context)

        del conversation[comment_id]

        IStatusMessage(self.context.REQUEST).addStatusMessage(
            _("Comment deleted."),
            type="info")

        return self.context.REQUEST.RESPONSE.redirect(self.context.REQUEST.HTTP_REFERER)

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

        IStatusMessage(self.context.REQUEST).addStatusMessage(
            _("Comment approved."),
            type="info")

        return self.context.REQUEST.RESPONSE.redirect(self.context.REQUEST.HTTP_REFERER)

class BulkActionsView(BrowserView):
    """Bulk actions (unapprove, approve, delete, mark as spam).
    """

    def __call__(self):

        context = aq_inner(self.context)

        if self.request.has_key('form.select.BulkAction'):

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
                    raise KeyError

    def retract(self):
        raise NotImplementedError

    def publish(self):
        context = aq_inner(self.context)
        for path in self.paths:
            comment = context.restrictedTraverse(path)
            portal_workflow = getToolByName(comment, 'portal_workflow')
            current_state = portal_workflow.getInfoFor(comment, 'review_state')
            if current_state != 'published':
                portal_workflow.doActionFor(comment, 'publish')
            catalog = getToolByName(comment, 'portal_catalog')
            catalog.reindexObject(comment)

    def mark_as_spam(self):
        raise NotImplementedError

    def delete(self):
        context = aq_inner(self.context)
        for path in self.paths:
            comment = context.restrictedTraverse(path)
            conversation = aq_parent(comment)
            del conversation[comment.id]
