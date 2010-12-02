# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel

from plone.registry.interfaces import IRegistry

from zope.component import getMultiAdapter, queryUtility

from z3c.form import button
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget

from plone.app.discussion.interfaces import IDiscussionSettings, _


class DiscussionSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IDiscussionSettings
    label = _(u"Discussion settings")
    description = _(u"help_discussion_settings_editform",
                    default=u"Some discussion related settings are not located "
                             "in the Discussion Control Panel.\n"
                             "To enable comments for a specific content type, " 
                             "go to the Types Control Panel of this type and "
                             "choose \"Allow comments\".\n"
                             "To enable the moderation workflow for comments, "
                             "go to the Types Control Panel, choose "
                             "\"Comment\" and set workflow to "
                             "\"Comment Review Workflow\".")

    def updateFields(self):
        super(DiscussionSettingsEditForm, self).updateFields()
        self.fields['globally_enabled'].widgetFactory = \
            SingleCheckBoxFieldWidget
        self.fields['anonymous_comments'].widgetFactory = \
            SingleCheckBoxFieldWidget
        self.fields['show_commenter_image'].widgetFactory = \
            SingleCheckBoxFieldWidget
        self.fields['moderator_notification_enabled'].widgetFactory = \
            SingleCheckBoxFieldWidget
        self.fields['user_notification_enabled'].widgetFactory = \
            SingleCheckBoxFieldWidget

    def updateWidgets(self):
        super(DiscussionSettingsEditForm, self).updateWidgets()
        self.widgets['globally_enabled'].label = _(u"Enable Comments")
        self.widgets['anonymous_comments'].label = _(u"Anonymous Comments")
        self.widgets['show_commenter_image'].label = _(u"Commenter Image")
        self.widgets['moderator_notification_enabled'].label = \
            _(u"Moderator Email Notification")
        self.widgets['user_notification_enabled'].label = \
            _(u"User Email Notification")

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"), 
                                                      "info")
        self.context.REQUEST.RESPONSE.redirect("@@discussion-settings")

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"), 
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), 
                                                  self.control_panel_view))

        
class DiscussionSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = DiscussionSettingsEditForm
    index = ViewPageTemplateFile('controlpanel.pt')

    def settings(self):
        """Compose a string that contains all registry settings that are
           needed for the discussion control panel.
        """
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
     
        output = []
        
        # Globally enabled
        if settings.globally_enabled:
            output.append("globally_enabled")
        
        # Anonymous comments
        if settings.anonymous_comments:
            output.append("anonymous_comments")
        
        # Invalid mail setting
        ctrlOverview = getMultiAdapter((self.context, self.request),
                                       name='overview-controlpanel')
        if ctrlOverview.mailhost_warning():
            output.append("invalid_mail_setup")

        # Workflow
        wftool = getToolByName(self.context, 'portal_workflow', None)
        discussion_workflow = wftool.getChainForPortalType('Discussion Item')[0]
        if discussion_workflow:
            output.append(discussion_workflow)
            
        # Merge all settings into one string
        return ' '.join(output)
