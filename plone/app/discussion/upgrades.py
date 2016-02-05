# -*- coding: utf-8 -*-
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


default_profile = 'profile-plone.app.discussion:default'


def update_registry(context):
    registry = getUtility(IRegistry)
    registry.registerInterface(IDiscussionSettings)


def update_rolemap(context):
    context.runImportStepFromProfile(default_profile, 'rolemap')
