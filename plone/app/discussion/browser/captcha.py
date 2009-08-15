from persistent import Persistent

from Products.CMFCore.utils import getToolByName

from z3c.form import validator
from z3c.form.field import Fields

from zope import interface, schema

from zope.annotation import factory

from zope.component import adapts, provideAdapter, queryUtility
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.interface import Interface, implements

from plone.registry.interfaces import IRegistry

from plone.z3cform.fieldsets import extensible
from plone.z3cform.fieldsets.interfaces import IFormExtender

from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.comment import Comment
from plone.app.discussion.interfaces import IDiscussionSettings, ICaptcha

from plone.app.discussion.browser.validator import CaptchaValidator

HAS_CAPTCHA = False
try:
    from plone.formwidget.captcha import CaptchaFieldWidget
    HAS_CAPTCHA = True
except ImportError:
    pass

HAS_RECAPTCHA = False
try:
    from plone.formwidget.recaptcha import ReCaptchaFieldWidget
    HAS_RECAPTCHA = True
except ImportError:
    pass

class Captcha(Persistent):
    interface.implements(ICaptcha)
    adapts(Comment)
    captcha = u""

Captcha = factory(Captcha)

if HAS_CAPTCHA or HAS_RECAPTCHA:
    # Extend the comment form with captcha, if a captcha solution is installed.
    class CaptchaExtender(extensible.FormExtender):
        adapts(Interface, IDefaultBrowserLayer, CommentForm) # context, request, form

        fields = Fields(ICaptcha)

        def __init__(self, context, request, form):
            self.context = context
            self.request = request
            self.form = form

            registry = queryUtility(IRegistry)
            settings = registry.forInterface(IDiscussionSettings)
            self.captcha = settings.captcha
            portal_membership = getToolByName(self.context, 'portal_membership')
            self.isAnon = portal_membership.isAnonymousUser()

        def update(self):
            if self.captcha != 'disabled' and self.isAnon:
                # Add captcha field if captcha is enabled in the registry
                self.add(ICaptcha, prefix="")
                if HAS_CAPTCHA and self.captcha == 'captcha':
                    # If Captcha is installed and Captcha is enabled,
                    # use the CaptchaFieldWidget
                    self.form.fields['captcha'].widgetFactory = CaptchaFieldWidget
                elif HAS_RECAPTCHA and self.captcha == 'recaptcha':
                    # If ReCaptcha is installed and ReCaptcha is enabled,
                    # use the ReCaptchaFieldWidget
                    self.form.fields['captcha'].widgetFactory = ReCaptchaFieldWidget

    # Register Captcha validator for the Captcha field in the ICaptcha Form
    validator.WidgetValidatorDiscriminators(CaptchaValidator, field=ICaptcha['captcha'])

else:
    # This is necessary, otherwise the zcml registration of the CaptchaExtender
    # would fail if no captcha solution is installed.
    class CaptchaExtender(extensible.FormExtender):
        adapts(Interface, IDefaultBrowserLayer, CommentForm)

        def __init__(self, context, request, form):
            pass

        def update(self):
            pass