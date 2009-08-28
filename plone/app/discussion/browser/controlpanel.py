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
    description = _(u"""Some discussion related settings are not located
                        in the Discussion Control Panel.

                        To enable moderation for content types, go to the
                        Types Control Panel, and enable moderation for a
                        specific content type.

                        To enable comment moderation, go to the Types
                        Control Panel, choose "Comment", and set the
                        workflow to "Comment Review Workflow".
                        """)

    def updateFields(self):
        super(DiscussionSettingsEditForm, self).updateFields()
        #self.fields['globally_enabled'].widgetFactory = SingleCheckBoxWidget

    def updateWidgets(self):
        super(DiscussionSettingsEditForm, self).updateWidgets()

class DiscussionSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = DiscussionSettingsEditForm
