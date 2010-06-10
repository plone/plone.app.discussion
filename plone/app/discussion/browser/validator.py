# -*- coding: utf-8 -*-

# Captcha validator, see captcha.txt for design notes.

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
    adapts(Interface, IDiscussionLayer, Interface, IField, Interface)
    #       Object, Request, Form, Field, Widget,
    # We adapt the CaptchaValidator class to all form fields (IField)

    def validate(self, value):
        super(CaptchaValidator, self).validate(value)

        data = self.request.form

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)

        if settings.captcha != 'disabled':
            captcha = getMultiAdapter((aq_inner(self.context), self.request), 
                                      name=settings.captcha)
            if not captcha.verify(input=value):
                raise WrongCaptchaCode
            else:
                return True
        
# Register Captcha validator for the Captcha field in the ICaptcha Form
validator.WidgetValidatorDiscriminators(CaptchaValidator, 
                                        field=ICaptcha['captcha'])
            