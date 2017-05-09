"""Catalog indexers, using plone.indexer. These will populate standard catalog
indexes with values based on the IComment interface.

Also provide event handlers to actually catalog the comments.
"""

from string import join

from DateTime import DateTime

from Products.CMFCore.interfaces import IContentish

from Products.CMFPlone.utils import safe_unicode

from Products.ZCatalog.interfaces import IZCatalog

from plone.app.discussion.interfaces import IConversation, IComment

from plone.indexer import indexer

from plone.uuid.interfaces import IUUID


MAX_DESCRIPTION = 25

# Conversation Indexers


@indexer(IContentish, IZCatalog)
def total_comments(object):
    # Total number of comments on a conversation
    # Indexers won't work on old discussion items
    if object.meta_type != 'Discussion Item':
        try:
            conversation = IConversation(object)
            public_comments = conversation.public_comments()
            if not public_comments:
                raise AttributeError
            return public_comments
        except TypeError:  # pragma: no cover
            # The item is contentish but nobody
            # implemented an adapter for it
            pass


@indexer(IContentish, IZCatalog)
def last_comment_date(object):
    # Date of the latest comment on a conversation
    # Indexers won't work on old discussion items
    if object.meta_type != 'Discussion Item':
        try:
            conversation = IConversation(object)
            last_comment_date = conversation.last_comment_date
            if not last_comment_date:
                raise AttributeError
            return last_comment_date
        except TypeError:  # pragma: no cover
            # The item is contentish but nobody
            # implemented an adapter for it
            pass


@indexer(IContentish, IZCatalog)
def commentators(object):
    # List of commentators on a conversation
    # Indexers won't work on old discussion items
    if object.meta_type != 'Discussion Item':
        try:
            conversation = IConversation(object)
            public_commentators = conversation.public_commentators
            if not public_commentators:
                raise AttributeError
            return conversation.public_commentators
        except TypeError:  # pragma: no cover
            # The item is contentish but nobody
            # implemented an adapter for it
            pass

# Comment Indexers


@indexer(IComment)
def title(object):
    return object.Title()


@indexer(IComment)
def creator(object):
    result = object.creator and safe_unicode(object.creator).encode('utf-8')
    if not result:
        raise AttributeError
    return result


@indexer(IComment)
def description(object):
    # Return the first 25 words of the comment text and append ' [...]'
    text = join(object.getText(
        targetMimetype='text/plain').split()[:MAX_DESCRIPTION])
    if len(object.getText().split()) > 25:
        text += " [...]"
    return text


@indexer(IComment)
def searchable_text(object):
    return object.getText(targetMimetype='text/plain')


@indexer(IComment)
def in_response_to(object):
    # Always returns the content object the comment is added to.
    # Do not confuse this with the in_reply_to attribute of a comment!
    return object.__parent__.__parent__.title_or_id()


@indexer(IComment)
def effective(object):
    # the catalog index needs Zope DateTime instead of Python datetime
    return DateTime(object.creation_date.year,
                    object.creation_date.month,
                    object.creation_date.day,
                    object.creation_date.hour,
                    object.creation_date.minute,
                    object.creation_date.second,
                    'GMT')


@indexer(IComment)
def created(object):
    # the catalog index needs Zope DateTime instead of Python datetime
    return DateTime(object.creation_date.year,
                    object.creation_date.month,
                    object.creation_date.day,
                    object.creation_date.hour,
                    object.creation_date.minute,
                    object.creation_date.second,
                    'GMT')


@indexer(IComment)
def modified(object):
    # the catalog index needs Zope DateTime instead of Python datetime
    return DateTime(object.modification_date.year,
                    object.modification_date.month,
                    object.modification_date.day,
                    object.modification_date.hour,
                    object.modification_date.minute,
                    object.modification_date.second,
                    'GMT')


# Override the conversation indexers for comments


@indexer(IComment)
def comments_total_comments(object):
    raise AttributeError


@indexer(IComment)
def comments_last_comment_date(object):
    raise AttributeError


@indexer(IComment)
def comments_commentators(object):
    raise AttributeError


# Make sure comments don't inherit their container's UID
@indexer(IComment)
def UID(object):
    if IUUID:
        iuuid = IUUID(object, None)
        if not iuuid:
            raise AttributeError
        return iuuid
