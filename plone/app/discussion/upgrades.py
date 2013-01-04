from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IDiscussionSettings


def update_registry(context):
    registry = getUtility(IRegistry)
    registry.registerInterface(IDiscussionSettings)


def add_anonymous_email_enabled_settings(context):
    registry = getUtility(IRegistry)
    key = 'plone.app.discussion.interfaces.IDiscussionSettings.'
    key += 'anonymous_email_enabled'
    registry[key] = False
