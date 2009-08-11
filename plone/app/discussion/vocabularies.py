from zope import interface
from zope import component
import zope.schema.interfaces
import zope.schema.vocabulary

# XXX: REPLACE THIS!!!
HAS_CAPTCHA=False
HAS_RECAPTCHA=False

try:
     from plone.formwidget.captcha.widget import CaptchaFieldWidget
     HAS_CAPTCHA = True
except ImportError:
    pass

try:
     from plone.formwidget.captcha.widget import ReCaptchaFieldWidget
     HAS_RECAPTCHA = True
except ImportError:
    pass
# XXX: REPLACE THIS!!!

def captcha_vocabulary(context):
    """Vocabulary with all available captcha implementations.
    """
    terms = []
    terms.append(
        zope.schema.vocabulary.SimpleTerm(
            value='disabled',
            token='disabled',
            title='Disabled'))

    if HAS_CAPTCHA:
        terms.append(
            zope.schema.vocabulary.SimpleTerm(
                value='captcha',
                token='captcha',
                title='Captcha'))
    if HAS_RECAPTCHA:
        terms.append(
            zope.schema.vocabulary.SimpleTerm(
                value='recaptcha',
                token='recaptcha',
                title='ReCaptcha'))
    return zope.schema.vocabulary.SimpleVocabulary(terms)

interface.alsoProvides(captcha_vocabulary,
                       zope.schema.interfaces.IVocabularyFactory)