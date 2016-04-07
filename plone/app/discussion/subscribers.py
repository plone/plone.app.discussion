# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName


def index_object(obj, event):
    """Index the object when it is added/modified to the conversation.
    """
    catalog = getToolByName(obj, 'portal_catalog')
    return catalog.reindexObject(obj)


def unindex_object(obj, event):
    """Unindex the object when it is removed from the conversation.
    """
    catalog = getToolByName(obj, 'portal_catalog')
    return catalog.unindexObject(obj)
