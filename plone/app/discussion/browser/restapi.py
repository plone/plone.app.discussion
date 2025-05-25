"""REST API integration for plone.app.discussion.

This module contains REST API control panel adapters that are only
registered when plone.restapi is available.
"""

from ..interfaces import _
from ..interfaces import IDiscussionSettings
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import Interface


@adapter(Interface, Interface)
class DiscussionControlPanel(RegistryConfigletPanel):
    """Volto-compatible REST API control panel for discussion settings."""

    schema = IDiscussionSettings
    schema_prefix = None
    configlet_id = "discussion"
    configlet_category_id = "plone-content"
    title = _("Discussion")
    group = "Content"
