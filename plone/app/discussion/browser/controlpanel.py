from Products.Five.browser import BrowserView

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from plone.app.registry.browser import controlpanel

from plone.app.discussion.interfaces import IDiscussionSettings, _

from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget


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
        self.fields['globally_enabled'].widgetFactory = SingleCheckBoxFieldWidget
        self.fields['anonymous_comments'].widgetFactory = SingleCheckBoxFieldWidget
        self.fields['show_commenter_image'].widgetFactory = SingleCheckBoxFieldWidget

    def updateWidgets(self):
        super(DiscussionSettingsEditForm, self).updateWidgets()
        self.widgets['globally_enabled'].label = u""
        self.widgets['anonymous_comments'].label = u""
        self.widgets['show_commenter_image'].label = u""


class DiscussionSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = DiscussionSettingsEditForm
