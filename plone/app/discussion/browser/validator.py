# -*- coding: utf-8 -*-
"""Captcha validator, see captcha.txt for design notes.
"""
from Acquisition import aq_inner
from plone.app.discussion.interfaces import ICaptcha
from plone.app.discussion.interfaces import IDiscussionLayer
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry
from z3c.form import validator
from z3c.form.interfaces import IValidator
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IField


try:
    from collective.z3cform.norobots.validator import WrongNorobotsAnswer
except ImportError:
    pass

try:
    from plone.formwidget.captcha.validator import WrongCaptchaCode
except ImportError:
    pass

try:
    from plone.formwidget.recaptcha.validator import WrongCaptchaCode  # noqa
except ImportError:
    pass


@implementer(IValidator)
@adapter(Interface, IDiscussionLayer, Interface, IField, Interface)
class CaptchaValidator(validator.SimpleFieldValidator):
    #       Object, Request, Form, Field, Widget,
    # We adapt the CaptchaValidator class to all form fields (IField)

    def validate(self, value):
        super(CaptchaValidator, self).validate(value)

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)

        if settings.captcha in ('captcha', 'recaptcha', 'norobots'):
            captcha = getMultiAdapter((aq_inner(self.context), self.request),
                                      name=settings.captcha)
            if not captcha.verify(input=value):
                if settings.captcha == 'norobots':
                    raise WrongNorobotsAnswer
                else:
                    raise WrongCaptchaCode
            else:
                return True


# Register Captcha validator for the Captcha field in the ICaptcha Form
validator.WidgetValidatorDiscriminators(CaptchaValidator,
                                        field=ICaptcha['captcha'])
