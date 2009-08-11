from persistent import Persistent

from z3c.form.field import Fields

from zope import interface, schema

from zope.annotation import factory
from zope.annotation.attribute import AttributeAnnotations

from zope.component import adapts, provideAdapter, queryUtility
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.interface import Interface, implements

from plone.registry.interfaces import IRegistry

from plone.z3cform.fieldsets import extensible
from plone.z3cform.fieldsets.interfaces import IFormExtender

from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.comment import Comment
from plone.app.discussion.interfaces import IDiscussionSettings

class ICaptcha(Interface):
    captcha = schema.TextLine(title=u"Captcha",
                              required=True)

class Captcha(Persistent):
    interface.implements(ICaptcha)
    adapts(Comment)
    captcha = u""

Captcha = factory(Captcha)
provideAdapter(Captcha)
provideAdapter(AttributeAnnotations)

class CaptchaExtender(extensible.FormExtender):
    adapts(Interface, IDefaultBrowserLayer, CommentForm) # context, request, form

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        self.captcha = settings.captcha

    def update(self):
        if self.captcha != 'disabled':
            # Add all fields from the captcha interface
            self.add(ICaptcha, prefix="")
            if self.captcha == 'captcha':
                self.form.fields['captcha'].widgetFactory = CaptchaFieldWidget
            elif self.captcha == 'recaptcha':
                self.form.fields['captcha'].widgetFactory = ReCaptchaFieldWidget