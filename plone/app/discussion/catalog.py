"""Catalog indexers, using plone.indexer. These will populate standard catalog
indexes with values based on the IComment interface.

Also provide event handlers to actually catalog the comments.
"""

from string import split, join

from plone.indexer import indexer

from plone.app.discussion.interfaces import IComment

MAX_DESCRIPTION=25

@indexer(IComment)
def comment_title(object):
    return object.title

@indexer(IComment)
def comment_description(object):
    # Return the first 25 words of the comment text and append '...'
    return '%s...' % join(object.text.split()[:MAX_DESCRIPTION])

@indexer(IComment)
def comment_searchable_text(object):
    return object.title, object.text

