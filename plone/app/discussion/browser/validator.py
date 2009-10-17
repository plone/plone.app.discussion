# Captcha/ReCaptcha validators. We override the standard validators from
# plone.formwidget.captcha and plone.formwidget.recaptcha, in order to
# switch between the two. This is necessary, because the zcml registration
# of the CaptchaValidator has to be there, no matter which captcha solution
# is installed, or even when no captcha solution is installed.

from Acquisition import aq_inner

from z3c.form import validator

from z3c.form.interfaces import IValidator

from zope.component import getMultiAdapter, provideAdapter, queryUtility

from zope.schema import ValidationError

from plone.registry.interfaces import IRegistry

from plone.app.discussion.interfaces import IDiscussionSettings, IDiscussionLayer, MessageFactory as _

from zope.interface import implements, Interface
from zope.schema.interfaces import IField
from zope.component import adapts

try:
    from plone.formwidget.captcha import CaptchaMessageFactory as _
    class WrongCaptchaCode(ValidationError):
        __doc__ = _("""The code you entered was wrong, please enter the new one.""")
except:
    pass

try:
    from plone.formwidget.recaptcha import ReCaptchaMessageFactory as _
    class WrongReCaptchaCode(ValidationError):
        __doc__ = _("""The code you entered was wrong, please enter the new one.""")
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
            captcha = getMultiAdapter((aq_inner(self.context), self.request), name='captcha')
            if value:
                if not captcha.verify(value):
                    raise WrongCaptchaCode
                else:
                    return True
            raise WrongCaptchaCode
        elif settings.captcha == 'recaptcha':
            # Fetch recatpcha view
            captcha = getMultiAdapter((aq_inner(self.context), self.request), name='recaptcha')
            if not captcha.verify():
                raise WrongReCaptchaCode
            else:
                return True