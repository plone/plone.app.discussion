# -*- coding: utf-8 -*-
"""The portal_discussion tool, usually accessed via
queryUtility(ICommentingTool). The default implementation delegates to the
standard portal_catalog for indexing comments.

BBB support for the old portal_discussion is provided in the bbb package.
"""
from interfaces import IComment
from interfaces import ICommentingTool
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject
from zope import interface
from zope.component import queryUtility


@interface.implementer(ICommentingTool)
class CommentingTool(UniqueObject, SimpleItem):

    meta_type = 'plone.app.discussion tool'
    id = 'portal_discussion'

    def reindexObject(self, object):
        # Reindex in catalog.
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.reindexObject(object)

    indexObject = reindexObject

    def unindexObject(self, object):
        # Remove from catalog.
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.unindexObject(object)

    def uniqueValuesFor(self, name):
        # return unique values for FieldIndex name
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.uniqueValuesFor(name)

    def searchResults(self, REQUEST=None, **kw):
        # Calls ZCatalog.searchResults with extra arguments that
        # limit the results to what the user is allowed to see.
        catalog = getToolByName(self, 'portal_catalog')
        object_provides = [IComment.__identifier__]

        if 'object_provides' in kw:
            kw_provides = kw['object_provides']
            if isinstance(str, kw_provides):
                object_provides.append(kw_provides)
            else:
                object_provides.extend(kw_provides)

        if REQUEST is not None and 'object_provides' in REQUEST.form:
            rq_provides = REQUEST.form['object_provides']
            del REQUEST.form['object_provides']
            if isinstance(str, rq_provides):
                object_provides.append(rq_provides)
            else:
                object_provides.extend(rq_provides)

        kw['object_provides'] = object_provides
        return catalog.searchResults(REQUEST, **kw)


def index_object(obj, event):
    """Index the object when added to the conversation
    """
    tool = queryUtility(ICommentingTool)
    if tool is not None:
        tool.indexObject(obj)


def unindex_object(obj, event):
    """Unindex the object when removed
    """
    tool = queryUtility(ICommentingTool)
    if tool is not None:
        tool.unindexObject(obj)
