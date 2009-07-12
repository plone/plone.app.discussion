from Products.Five.browser import BrowserView

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from plone.app.registry.browser import controlpanel

from plone.app.discussion.interfaces import IDiscussionSettings, _

try:
    # only in z3c.form 2.0
    from z3c.form.browser.textlines import TextLinesFieldWidget
    from z3c.form.browser.widget import SingleCheckBoxWidget
except ImportError:
    from plone.z3cform.textlines import TextLinesFieldWidget
    from plone.z3cform.widget import SingleCheckBoxWidget

class DiscussionSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IDiscussionSettings
    label = _(u"Discussion settings")
    description = _(u"Please enter the options specified")

    def updateFields(self):
        super(DiscussionSettingsEditForm, self).updateFields()
        #self.fields['globally_enabled'].widgetFactory = SingleCheckBoxWidget

    def updateWidgets(self):
        super(DiscussionSettingsEditForm, self).updateWidgets()

class DiscussionSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = DiscussionSettingsEditForm

class Utility(BrowserView):
    """Utility view to determine ...
    """

    def globally_enabled(self):
        """Determine if the utility is enabled and we are in an enabled domain
        """

        registry = queryUtility(IRegistry)
        if registry is None:
            return False

        settings = None
        try:
            settings = registry.forInterface(IDiscussionSettings)
        except KeyError:
            return False

        if not settings.globally_enabled:
            return False
        else:
            return True

        return False
