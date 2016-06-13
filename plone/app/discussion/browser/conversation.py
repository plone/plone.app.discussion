# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Acquisition import aq_chain
from Acquisition import aq_inner
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_hasattr
from zope.component import queryUtility


try:
    from plone.dexterity.interfaces import IDexterityContent
    DEXTERITY_INSTALLED = True
except ImportError:
    DEXTERITY_INSTALLED = False


def traverse_parents(context):
    # Run through the aq_chain of obj and check if discussion is
    # enabled in a parent folder.
    for obj in aq_chain(context):
        if not IPloneSiteRoot.providedBy(obj):
            obj_is_folderish = IFolderish.providedBy(obj)
            obj_is_stuctural = not INonStructuralFolder.providedBy(obj)
            if (obj_is_folderish and obj_is_stuctural):
                flag = getattr(obj, 'allow_discussion', None)
                if flag is not None:
                    return flag
    return None


class ConversationView(object):

    def enabled(self):
        if DEXTERITY_INSTALLED and IDexterityContent.providedBy(self.context):
            return self._enabled_for_dexterity_types()
        else:
            return self._enabled_for_archetypes()

    def _enabled_for_archetypes(self):
        """ Returns True if discussion is enabled for this conversation.

        This method checks five different settings in order to figure out if
        discussion is enabled on a specific content object:

        1) Check if discussion is enabled globally in the plone.app.discussion
           registry/control panel.

        2) If the current content object is a folder, always return
           False, since we don't allow comments on a folder. This
           setting is used to allow / disallow comments for all content
           objects inside a folder, not for the folder itself.

        3) Check if the allow_discussion boolean flag on the content object is
           set. If it is set to True or False, return the value. If it set to
           None, try further.

        4) Traverse to a folder with allow_discussion set to either True or
           False. If allow_discussion is not set (None), traverse further until
           we reach the PloneSiteRoot.

        5) Check if discussion is allowed for the content type.
        """
        context = aq_inner(self.context)

        # Fetch discussion registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)

        # Check if discussion is allowed globally
        if not settings.globally_enabled:
            return False

        # Always return False if object is a folder
        context_is_folderish = IFolderish.providedBy(context)
        if context_is_folderish:
            if not INonStructuralFolder.providedBy(context):
                return False

        # If discussion is disabled for the object, bail out
        obj_flag = getattr(aq_base(context), 'allow_discussion', None)
        if obj_flag is False:
            return False

        # Check if traversal returned a folder with discussion_allowed set
        # to True or False.
        folder_allow_discussion = traverse_parents(context)

        if folder_allow_discussion:
            if not getattr(self, 'allow_discussion', None):
                return True
        else:
            if obj_flag:
                return True

        # Check if discussion is allowed on the content type
        portal_types = getToolByName(self, 'portal_types')
        document_fti = getattr(portal_types, context.portal_type)
        if not document_fti.getProperty('allow_discussion'):
            # If discussion is not allowed on the content type,
            # check if 'allow discussion' is overridden on the content object.
            if not obj_flag:
                return False

        return True

    def _enabled_for_dexterity_types(self):
        """ Returns True if discussion is enabled for this conversation.

        This method checks five different settings in order to figure out if
        discussion is enable on a specific content object:

        1) Check if discussion is enabled globally in the plone.app.discussion
           registry/control panel.

        2) Check if the allow_discussion boolean flag on the content object is
           set. If it is set to True or False, return the value. If it set to
           None, try further.

        3) Check if discussion is allowed for the content type.
        """
        context = aq_inner(self.context)

        # Fetch discussion registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)

        # Check if discussion is allowed globally
        if not settings.globally_enabled:
            return False

        # Check if discussion is allowed on the content object
        if safe_hasattr(context, 'allow_discussion'):
            if context.allow_discussion is not None:
                return context.allow_discussion

        # Check if discussion is allowed on the content type
        portal_types = getToolByName(self, 'portal_types')
        document_fti = getattr(portal_types, context.portal_type)
        return document_fti.getProperty('allow_discussion')
