from Products.Five.browser import BrowserView

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from plone.app.registry.browser import controlpanel

from plone.app.discussion.interfaces import IDiscussionSettings, _

from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget


class DiscussionSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IDiscussionSettings
    label = _(u"Discussion settings")
    description = _(u"help_discussion_settings_editform",
                    default=u"Some discussion related settings are not located "
                             "in the Discussion Control Panel.\n"
                             "To enable comments for a specific content type, " 
                             "go to the Types Control Panel of this type and "
                             "choose 'enable moderation'.\n"
                             "To enable the moderation workflow for comments, "
                             "go to the Types Control Panel, choose \"Comment\" "
                             "and set workflow to \"Comment Review Workflow\".")

    def updateFields(self):
        super(DiscussionSettingsEditForm, self).updateFields()
        self.fields['globally_enabled'].widgetFactory = SingleCheckBoxFieldWidget
        self.fields['anonymous_comments'].widgetFactory = SingleCheckBoxFieldWidget
        self.fields['show_commenter_image'].widgetFactory = SingleCheckBoxFieldWidget
        self.fields['moderator_notification_enabled'].widgetFactory = SingleCheckBoxFieldWidget
        #self.fields['user_notification_enabled'].widgetFactory = SingleCheckBoxFieldWidget

    def updateWidgets(self):
        super(DiscussionSettingsEditForm, self).updateWidgets()
        self.widgets['globally_enabled'].label = _(u"Enable Comments")
        self.widgets['anonymous_comments'].label = _(u"Anonymous Comments")
        self.widgets['show_commenter_image'].label = _(u"Commenter Image")
        self.widgets['moderator_notification_enabled'].label = _(u"Moderator Email Notification")
        #self.widgets['user_notification_enabled'].label = _(u"User Email Notification")


class DiscussionSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = DiscussionSettingsEditForm
