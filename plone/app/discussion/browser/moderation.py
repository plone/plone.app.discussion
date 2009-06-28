from plone.app.content.browser.tableview import Table, TableKSSView

from Acquisition import aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.app.pagetemplate import ViewPageTemplateFile as VPTF

from Products.CMFCore.utils import getToolByName

from zope.component import getMultiAdapter
from zope.interface import implements
from zope.i18n import translate

from AccessControl import Unauthorized
from Acquisition import aq_parent, aq_inner
from OFS.interfaces import IOrderedContainer
from Products.ATContentTypes.interface import IATTopic
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView

from plone.memoize import instance
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.content.browser.tableview import Table, TableKSSView

from Products.CMFPlone.interfaces import IPloneSiteRoot

import urllib

class View(BrowserView):
    """Moderation View
    """

    template = ViewPageTemplateFile('moderation.pt')

    def contents_table(self):
        table = ReviewCommentsTable(aq_inner(self.context), self.request)
        return table.render()

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

class ReviewTable(Table):
    render = VPTF("table.pt")
    batching = VPTF("batching.pt")

class ReviewCommentsTable(object):
    """The reviewcomments table renders the table and its actions.
    """

    def __init__(self, context, request, contentFilter={}):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter

        url = context.absolute_url()
        view_url = url + '/@@moderate-comments'
        self.table = ReviewTable(request, url, view_url, self.items)

    def render(self):
        return self.table.render()

    @property
    def items(self):
        """
        """
        context = aq_inner(self.context)

        self.state = self.request.get('review_state', 'pending')
        self.transition = self.request.get('publish_transition', 'pending')
        self.limit = self.request.get('limit', 100)

        catalog = getToolByName(context, 'portal_catalog')

        brains = catalog(
                portal_type='Discussion Item',
                sort_on='created',
                sort_limit=self.limit,
            )

        plone_utils = getToolByName(context, 'plone_utils')
        plone_view = getMultiAdapter((context, self.request), name=u'plone')
        portal_workflow = getToolByName(context, 'portal_workflow')
        portal_properties = getToolByName(context, 'portal_properties')
        portal_types = getToolByName(context, 'portal_types')
        site_properties = portal_properties.site_properties

        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
        browser_default = context.browserDefault()

        results = []

        for i, obj in enumerate(brains):
            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = obj.getURL()
            path = obj.getPath or "/".join(obj.getPhysicalPath())
            icon = plone_view.getIcon(obj);

            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = obj.getURL(relative=True)

            type_title_msgid = portal_types[obj.portal_type].Title()
            url_href_title = u'%s: %s' % (translate(type_title_msgid,
                                                    context=self.request),
                                          safe_unicode(obj.Description))

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format=1)

            obj_type = obj.Type
            #if obj_type in use_view_action:
            #    view_url = url + '/view'
            #elif obj.is_folderish:
            #    view_url = url + "/moderate-comments"
            #else:
            #    view_url = url
            view_url = url + "/@@moderate-comments"

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])

            results.append(dict(
                url = url,
                url_href_title = url_href_title,
                id  = obj.getId,
                quoted_id = urllib.quote_plus(obj.getId),
                path = path,
                title_or_id = obj.pretty_title_or_id(),
                obj_type = obj_type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                wf_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                table_row_class = table_row_class,
                is_expired = context.isExpired(obj),
            ))
        return results

    @property
    def orderable(self):
        """
        """
        return IOrderedContainer.providedBy(aq_inner(self.context))

    @property
    def show_sort_column(self):
        return self.orderable and self.editable

    @property
    def editable(self):
        """
        """
        context_state = getMultiAdapter((aq_inner(self.context), self.request),
                                        name=u'plone_context_state')
        return context_state.is_editable()

    @property
    def buttons(self):
        buttons = []
        context = aq_inner(self.context)
        portal_actions = getToolByName(context, 'portal_actions')
        button_actions = portal_actions.listActionInfos(object=context, categories=('folder_buttons', ))

        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if not len(self.items):
            if self.context.cb_dataValid():
                for button in button_actions:
                    if button['id'] == 'paste':
                        return [self.setbuttonclass(button)]
            else:
                return []

        for button in button_actions:
            # Make proper classes for our buttons
            if button['id'] != 'paste' or context.cb_dataValid():
                buttons.append(self.setbuttonclass(button))
        return buttons

    def setbuttonclass(self, button):
        if button['id'] == 'paste':
            button['cssclass'] = 'standalone'
        else:
            button['cssclass'] = 'context'
        return button



class ReviewCommentsKSSView(TableKSSView):
    table = ReviewCommentsTable


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

        return self.context.REQUEST.RESPONSE.redirect(self.context.REQUEST.HTTP_REFERER)

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
