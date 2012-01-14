# -*- coding: utf-8 -*-
"""Captcha validator, see captcha.txt for design notes.
"""

from Acquisition import aq_inner

from z3c.form import validator

from z3c.form.interfaces import IValidator

from zope.component import getMultiAdapter, queryUtility

from zope.interface import implements, Interface

from zope.schema.interfaces import IField
from zope.component import adapts

from plone.registry.interfaces import IRegistry

from plone.app.discussion.interfaces import ICaptcha
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IDiscussionLayer

try:
    from collective.z3cform.norobots.validator import WrongNorobotsAnswer
except ImportError:
    pass

try:
    from plone.formwidget.captcha.validator import WrongCaptchaCode
except ImportError:
    pass

try:
    from plone.formwidget.recaptcha.validator import WrongCaptchaCode
except ImportError:
    pass


class CaptchaValidator(validator.SimpleFieldValidator):
    implements(IValidator)
    adapts(Interface, IDiscussionLayer, Interface, IField, Interface)
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
