from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IDiscussionSettings


def update_registry(context):
    registry = getUtility(IRegistry)
    registry.registerInterface(IDiscussionSettings)
