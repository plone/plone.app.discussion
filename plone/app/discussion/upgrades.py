from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IDiscussionSettings

default_profile = 'profile-plone.app.discussion:default'


def update_registry(context):
    registry = getUtility(IRegistry)
    registry.registerInterface(IDiscussionSettings)


def update_rolemap(context):
    context.runImportStepFromProfile(default_profile, 'rolemap')
