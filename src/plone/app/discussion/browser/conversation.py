from ..interfaces import IDiscussionSettings
from Acquisition import aq_chain
from Acquisition import aq_inner
from plone.base.interfaces import INonStructuralFolder
from plone.base.interfaces import IPloneSiteRoot
from plone.base.utils import safe_hasattr
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility


def traverse_parents(context):
    # Run through the aq_chain of obj and check if discussion is
    # enabled in a parent folder.
    for obj in aq_chain(context):
        if not IPloneSiteRoot.providedBy(obj):
            obj_is_folderish = IFolderish.providedBy(obj)
            obj_is_stuctural = not INonStructuralFolder.providedBy(obj)
            if obj_is_folderish and obj_is_stuctural:
                flag = getattr(obj, "allow_discussion", None)
                if flag is not None:
                    return flag
    return None


class ConversationView:
    def enabled(self):
        """Returns True if discussion is enabled for this conversation.

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
        if safe_hasattr(context, "allow_discussion"):
            if context.allow_discussion is not None:
                return context.allow_discussion

        # Check if discussion is allowed on the content type
        portal_types = getToolByName(self, "portal_types")
        document_fti = getattr(portal_types, context.portal_type)
        return document_fti.getProperty("allow_discussion")
