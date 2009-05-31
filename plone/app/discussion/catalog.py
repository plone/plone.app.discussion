"""Catalog indexers, using plone.indexer. These will populate standard catalog
indexes with values based on the IComment interface.

Also provide event handlers to actually catalog the comments.
"""

from plone.indexer import indexer

from plone.app.discussion.interfaces import IComment

@indexer(IComment)
def comment_title(object):
    return object.title

@indexer(IComment)
def comment_searchable_text(object):
    return object.title, object.text

