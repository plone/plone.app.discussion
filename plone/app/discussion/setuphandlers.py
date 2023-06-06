from Products.CMFCore.utils import getToolByName


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


def add_discussion_behavior_to_default_types(context):
    """Add the discussion behavior to all default types, if they exist."""
    types_tool = getToolByName(context, "portal_types")
    for type_name in DEFAULT_TYPES:
        if type_name in types_tool.objectIds():
            types_tool[type_name].behaviors += ("plone.allowdiscussion",)


def post_install(context):
    """Post install script"""
    add_discussion_behavior_to_default_types(context)
