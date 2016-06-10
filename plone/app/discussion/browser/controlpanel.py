# -*- coding: utf-8 -*-
from plone.app.controlpanel.interfaces import IConfigurationChangedEvent
from plone.app.discussion.interfaces import _
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.upgrades import update_registry
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRecordModifiedEvent
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import getSite


class DiscussionSettingsEditForm(controlpanel.RegistryEditForm):
    """Discussion settings form.
    """
    schema = IDiscussionSettings
    id = 'DiscussionSettingsEditForm'
    label = _(u'Discussion settings')
    description = _(
        u'help_discussion_settings_editform',
        default=u'Some discussion related settings are not '
                u'located in the Discussion Control Panel.\n'
                u'To enable comments for a specific content type, '
                u'go to the Types Control Panel of this type and '
                u'choose "Allow comments".\n'
                u'To enable the moderation workflow for comments, '
                u'go to the Types Control Panel, choose '
                u'"Comment" and set workflow to '
                u'"Comment Review Workflow".'
    )

    def updateFields(self):
        super(DiscussionSettingsEditForm, self).updateFields()
        self.fields['globally_enabled'].widgetFactory = \
            SingleCheckBoxFieldWidget
        self.fields['moderation_enabled'].widgetFactory = \
            SingleCheckBoxFieldWidget
        self.fields['edit_comment_enabled'].widgetFactory = \
            SingleCheckBoxFieldWidget
        self.fields['delete_own_comment_enabled'].widgetFactory = \
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
        try:
            super(DiscussionSettingsEditForm, self).updateWidgets()
        except KeyError:
            # upgrade profile not visible in prefs_install_products_form
            # provide auto-upgrade
            update_registry(self.context)
            super(DiscussionSettingsEditForm, self).updateWidgets()
        self.widgets['globally_enabled'].label = _(u'Enable Comments')
        self.widgets['anonymous_comments'].label = _(u'Anonymous Comments')
        self.widgets['show_commenter_image'].label = _(u'Commenter Image')
        self.widgets['moderator_notification_enabled'].label = _(
            u'Moderator Email Notification'
        )
        self.widgets['user_notification_enabled'].label = _(
            u'User Email Notification'
        )

    @button.buttonAndHandler(_('Save'), name=None)
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u'Changes saved'),
                                                      'info')
        self.context.REQUEST.RESPONSE.redirect('@@discussion-controlpanel')

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u'Edit cancelled'),
                                                      'info')
        self.request.response.redirect(
            '{0}/{1}'.format(
                self.context.absolute_url(),
                self.control_panel_view
            )
        )


class DiscussionSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """Discussion settings control panel.
    """
    form = DiscussionSettingsEditForm
    index = ViewPageTemplateFile('controlpanel.pt')

    @property
    def site_url(self):
        """Return the absolute URL to the current site, which is likely not
        necessarily the portal root.
        """
        return getSite().absolute_url()

    def settings(self):
        """Compose a string that contains all registry settings that are
           needed for the discussion control panel.
        """
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        wftool = getToolByName(self.context, 'portal_workflow', None)
        workflow_chain = wftool.getChainForPortalType('Discussion Item')
        output = []

        # Globally enabled
        if settings.globally_enabled:
            output.append('globally_enabled')

        # Comment moderation
        one_state_worklow_disabled = 'one_state_workflow' not in workflow_chain
        comment_review_workflow_disabled = \
            'comment_review_workflow' not in workflow_chain
        if one_state_worklow_disabled and comment_review_workflow_disabled:
            output.append('moderation_custom')
        elif settings.moderation_enabled:
            output.append('moderation_enabled')

        if settings.edit_comment_enabled:
            output.append('edit_comment_enabled')

        if settings.delete_own_comment_enabled:
            output.append('delete_own_comment_enabled')

        # Anonymous comments
        if settings.anonymous_comments:
            output.append('anonymous_comments')

        # Invalid mail setting
        ctrlOverview = getMultiAdapter((self.context, self.request),
                                       name='overview-controlpanel')
        if ctrlOverview.mailhost_warning():
            output.append('invalid_mail_setup')

        # Workflow
        if workflow_chain:
            discussion_workflow = workflow_chain[0]
            output.append(discussion_workflow)

        # Merge all settings into one string
        return ' '.join(output)

    def mailhost_warning(self):
        """Returns true if mailhost is not configured properly.
        """
        # Copied from Products.CMFPlone/controlpanel/browser/overview.py
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix='plone')
        mailhost = mail_settings.smtp_host
        email = mail_settings.email_from_address
        if mailhost and email:
            return False
        return True

    def custom_comment_workflow_warning(self):
        """Returns a warning string if a custom comment workflow is enabled.
        """
        wftool = getToolByName(self.context, 'portal_workflow', None)
        workflow_chain = wftool.getChainForPortalType('Discussion Item')
        one_state_workflow_enabled = 'one_state_workflow' in workflow_chain
        comment_review_workflow_enabled = \
            'comment_review_workflow' in workflow_chain
        if one_state_workflow_enabled or comment_review_workflow_enabled:
            return
        return True


def notify_configuration_changed(event):
    """Event subscriber that is called every time the configuration changed.
    """
    portal = getSite()
    wftool = getToolByName(portal, 'portal_workflow', None)

    if IRecordModifiedEvent.providedBy(event):
        # Discussion control panel setting changed
        if event.record.fieldName == 'moderation_enabled':
            # Moderation enabled has changed
            if event.record.value is True:
                # Enable moderation workflow
                wftool.setChainForPortalTypes(('Discussion Item',),
                                              'comment_review_workflow')
            else:
                # Disable moderation workflow
                wftool.setChainForPortalTypes(('Discussion Item',),
                                              'one_state_workflow')

    if IConfigurationChangedEvent.providedBy(event):
        # Types control panel setting changed
        if 'workflow' in event.data:
            registry = queryUtility(IRegistry)
            settings = registry.forInterface(IDiscussionSettings, check=False)
            workflow_chain = wftool.getChainForPortalType('Discussion Item')
            if workflow_chain:
                workflow = workflow_chain[0]
                if workflow == 'one_state_workflow':
                    settings.moderation_enabled = False
                elif workflow == 'comment_review_workflow':
                    settings.moderation_enabled = True
                else:
                    # Custom workflow
                    pass
