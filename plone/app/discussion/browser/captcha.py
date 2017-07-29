# -*- coding: utf-8 -*-
# Captcha validator, see captcha.txt for design notes.
from persistent import Persistent
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.comment import Comment
from plone.app.discussion.interfaces import ICaptcha
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry
from plone.z3cform.fieldsets import extensible
from Products.CMFCore.utils import getToolByName
from z3c.form import interfaces
from z3c.form.field import Fields
from zope import interface
from zope.annotation import factory
from zope.component import adapter
from zope.component import queryUtility
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


@adapter(Comment)
@interface.implementer(ICaptcha)
class Captcha(Persistent):
    """Captcha input field.
    """
    captcha = u''


Captcha = factory(Captcha)


# context, request, form
@adapter(Interface, IDefaultBrowserLayer, CommentForm)
class CaptchaExtender(extensible.FormExtender):
    """Extends the comment form with a Captcha. This Captcha extender is only
    registered when a plugin is installed that provides the
    "plone.app.discussion-captcha" feature.
    """

    fields = Fields(ICaptcha)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        self.captcha = settings.captcha
        portal_membership = getToolByName(self.context, 'portal_membership')
        self.isAnon = portal_membership.isAnonymousUser()

    def update(self):
        if self.captcha != 'disabled' and self.isAnon:
            # Add a captcha field if captcha is enabled in the registry
            self.add(ICaptcha, prefix='')
            if self.captcha == 'captcha':
                from plone.formwidget.captcha import CaptchaFieldWidget
                self.form.fields['captcha'].widgetFactory = CaptchaFieldWidget
            elif self.captcha == 'recaptcha':
                from plone.formwidget.recaptcha import ReCaptchaFieldWidget
                self.form.fields['captcha'].widgetFactory = \
                    ReCaptchaFieldWidget
            elif self.captcha == 'norobots':
                from collective.z3cform.norobots import NorobotsFieldWidget
                self.form.fields['captcha'].widgetFactory = NorobotsFieldWidget
            else:
                self.form.fields['captcha'].mode = interfaces.HIDDEN_MODE
