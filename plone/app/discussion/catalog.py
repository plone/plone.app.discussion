"""Catalog indexers, using plone.indexer. These will populate standard catalog
indexes with values based on the IComment interface.

Also provide event handlers to actually catalog the comments.
"""

from string import join

from DateTime import DateTime

from Products.CMFCore.interfaces import IContentish

from Products.ZCatalog.interfaces import IZCatalog

from plone.app.discussion.interfaces import IConversation, IComment

from plone.indexer import indexer

MAX_DESCRIPTION=25

# Conversation Indexers

@indexer(IContentish, IZCatalog)
def total_comments(object):
    # Total number of comments on a conversation
    # Indexers won't work on old discussion items
    if object.meta_type != 'Discussion Item':

        conversation = IConversation(object)
        return conversation.total_comments

@indexer(IContentish, IZCatalog)
def last_comment_date(object):
    # Date of the latest comment on a conversation
    # Indexers won't work on old discussion items
    if object.meta_type != 'Discussion Item':
        conversation = IConversation(object)
        return conversation.last_comment_date

@indexer(IContentish, IZCatalog)
def commentators(object):
    # List of commentators on a conversation
    # Indexers won't work on old discussion items
    if object.meta_type != 'Discussion Item':
        conversation = IConversation(object)
        return tuple(conversation.commentators.keys())

# Comment Indexers

@indexer(IComment)
def title(object):
    return object.title

@indexer(IComment)
def creator(object):
    return object.creator

@indexer(IComment)
def description(object):
    # Return the first 25 words of the comment text and append ' [...]'
    text = join(object.text.split()[:MAX_DESCRIPTION])
    if len(object.text.split()) > 25:
        text += " [...]"
    return text

@indexer(IComment)
def searchable_text(object):
    return object.title, object.text

@indexer(IComment)
def in_response_to(object):
    # Always returns the content object the comment is added to.
    # Do not confuse this with the in_reply_to attribute of a comment!
    return object.__parent__.__parent__.title_or_id()

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

# Override the conversation indexers for comments

@indexer(IComment)
def comments_total_comments(object):
    return None

@indexer(IComment)
def comments_last_comment_date(object):
    return None

@indexer(IComment)
def comments_commentators(object):
    return None
