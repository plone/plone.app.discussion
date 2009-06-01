"""Catalog indexers, using plone.indexer. These will populate standard catalog
indexes with values based on the IComment interface.

Also provide event handlers to actually catalog the comments.
"""

from string import split, join

from DateTime import DateTime

from plone.indexer import indexer

from plone.app.discussion.interfaces import IComment

MAX_DESCRIPTION=25

@indexer(IComment)
def comment_title(object):
    return object.title

@indexer(IComment)
def comment_creator(object):
    return object.creator

@indexer(IComment)
def comment_description(object):
    # Return the first 25 words of the comment text and append '...'
    return '%s...' % join(object.text.split()[:MAX_DESCRIPTION])

@indexer(IComment)
def comment_searchable_text(object):
    return object.title, object.text

@indexer(IComment)
def effective(object):
    # the catalog index needs Zope DateTime instead of Python datetime
    # Todo!!!
    return DateTime

@indexer(IComment)
def created(object):
    # the catalog index needs Zope DateTime instead of Python datetime
    return DateTime(object.creation_date.year,
                    object.creation_date.month,
                    object.creation_date.day,
                    object.creation_date.hour,
                    object.creation_date.minute,
                    object.creation_date.second)

@indexer(IComment)
def modified(object):
    # the catalog index needs Zope DateTime instead of Python datetime
    return DateTime(object.modification_date.year,
                    object.modification_date.month,
                    object.modification_date.day,
                    object.modification_date.hour,
                    object.modification_date.minute,
                    object.modification_date.second)
