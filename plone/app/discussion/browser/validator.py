# -*- coding: utf-8 -*-

from Acquisition import aq_inner

from z3c.form import validator

from z3c.form.interfaces import IValidator

from zope.component import getMultiAdapter, provideAdapter, queryUtility

from zope.schema import ValidationError

from zope.interface import implements, Interface
from zope.schema.interfaces import IField
from zope.component import adapts

from plone.registry.interfaces import IRegistry

from plone.app.discussion.interfaces import ICaptcha
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IDiscussionLayer
from plone.app.discussion.interfaces import MessageFactory as _

try:
    from plone.formwidget.captcha.validator import WrongCaptchaCode
except:
    pass

try:
    from plone.formwidget.recaptcha.validator import WrongCaptchaCode
except:
    pass

from zope.interface import implements, Interface
from zope.schema.interfaces import IField
from zope.component import adapts


class CaptchaValidator(validator.SimpleFieldValidator):
    implements(IValidator)
    adapts(Interface,IDiscussionLayer,Interface,IField,Interface)
    #       Object, Request, Form, Field, Widget,

    def validate(self, value):
        super(CaptchaValidator, self).validate(value)

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)

        if settings.captcha == 'captcha':
            # Fetch captcha view
            captcha = getMultiAdapter((aq_inner(self.context), self.request), 
                                      name='captcha')
            if value:
                if not captcha.verify(value):
                    raise WrongCaptchaCode
                else:
                    return True
            raise WrongCaptchaCode
        elif settings.captcha == 'recaptcha':
            # Fetch recaptcha view
            captcha = getMultiAdapter((aq_inner(self.context), self.request), 
                                      name='recaptcha')
            if not captcha.verify():
                raise WrongCaptchaCode
            else:
                return True

# Register Captcha validator for the Captcha field in the ICaptcha Form
validator.WidgetValidatorDiscriminators(CaptchaValidator, 
                                        field=ICaptcha['captcha'])            