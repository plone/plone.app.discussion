# -*- coding: utf-8 -*-

# Captcha validator, see captcha.txt for design notes.

from persistent import Persistent

from Products.CMFCore.utils import getToolByName

from z3c.form import interfaces, validator
from z3c.form.field import Fields

from zope import interface, schema

from zope.annotation import factory

from zope.component import adapts, provideAdapter, getUtility
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.interface import Interface, implements

from plone.registry.interfaces import IRegistry

from plone.z3cform.fieldsets import extensible
from plone.z3cform.fieldsets.interfaces import IFormExtender

from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.comment import Comment
from plone.app.discussion.interfaces import IDiscussionSettings, ICaptcha

from plone.app.discussion.browser.validator import CaptchaValidator


class Captcha(Persistent):
    """Captcha input field.
    """
    interface.implements(ICaptcha)
    adapts(Comment)
    captcha = u""

Captcha = factory(Captcha)


class CaptchaExtender(extensible.FormExtender):
    """Extends the comment form with a Captcha. This Captcha extender is only
    registered when a plugin is installed that provides the 
    "plone.app.discussion-captcha" feature.
    """
    adapts(Interface, IDefaultBrowserLayer, CommentForm) # context, request, form

    fields = Fields(ICaptcha)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        self.captcha = settings.captcha
        portal_membership = getToolByName(self.context, 'portal_membership')
        self.isAnon = portal_membership.isAnonymousUser()

    def update(self):
        if self.captcha != 'disabled' and self.isAnon:
            # Add a captcha field if captcha is enabled in the registry
            self.add(ICaptcha, prefix="")
            if self.captcha == 'captcha':
                from plone.formwidget.captcha import CaptchaFieldWidget
                self.form.fields['captcha'].widgetFactory = CaptchaFieldWidget
            elif self.captcha == 'recaptcha':
                from plone.formwidget.recaptcha import ReCaptchaFieldWidget
                self.form.fields['captcha'].widgetFactory = ReCaptchaFieldWidget
            elif self.captcha == 'akismet':
                # Hide the captcha field and move the Akismet validator error 
                # message to the top
                self.form.fields['captcha'].mode = interfaces.HIDDEN_MODE
                self.move('captcha', before='author_name', prefix='')
                