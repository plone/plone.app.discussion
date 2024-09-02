from plone.base.interfaces import INonInstallable
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer


DEFAULT_TYPES = [
    "Document",
    "Event",
    "File",
    "Folder",
    "Image",
    "News Item",
    "Collection",
    "Link",
]

BEHAVIOR = "plone.allowdiscussion"


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        return [
            "plone.app.discussion:to_3000",
        ]


def add_discussion_behavior_to_default_types(context):
    """Add the discussion behavior to all default types, if they exist."""
    types_tool = getToolByName(context, "portal_types")
    for type_name in DEFAULT_TYPES:
        if (
            type_name in types_tool.objectIds()
            and BEHAVIOR not in types_tool[type_name].behaviors
        ):
            types_tool[type_name].behaviors += (BEHAVIOR,)


def remove_discussion_behavior_to_default_types(context):
    """Remove the discussion behavior from all default types, if they exist."""
    types_tool = getToolByName(context, "portal_types")
    for type_name in types_tool.objectIds():
        fti = types_tool[type_name]
        if getattr(fti, "behaviors", None) is None:
            continue
        if BEHAVIOR in fti.behaviors:
            behaviors = list(fti.behaviors)
            behaviors.remove(BEHAVIOR)
            fti.behaviors = tuple(behaviors)


def post_install(context):
    """Post install script"""
    add_discussion_behavior_to_default_types(context)


def post_uninstall(context):
    """Post uninstall script"""
    remove_discussion_behavior_to_default_types(context)
