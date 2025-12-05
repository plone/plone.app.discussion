from plone.app.discussion.interfaces import _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


BAN_TYPE_COOLDOWN = "cooldown"
BAN_TYPE_SHADOW = "shadow"
BAN_TYPE_PERMANENT = "permanent"

HAS_CAPTCHA = False
try:
    import plone.formwidget.captcha  # noqa

    HAS_CAPTCHA = True  # pragma: no cover
except ImportError:
    pass

HAS_RECAPTCHA = False
try:
    import plone.formwidget.recaptcha  # noqa

    HAS_RECAPTCHA = True  # pragma: no cover
except ImportError:
    pass

HAS_HCAPTCHA = False
try:
    import plone.formwidget.hcaptcha  # noqa

    HAS_HCAPTCHA = True  # pragma: no cover
except ImportError:
    pass

HAS_AKISMET = False
try:
    import collective.akismet  # noqa

    HAS_AKISMET = True  # pragma: no cover
except ImportError:
    pass

HAS_NOROBOTS = False
try:
    import collective.z3cform.norobots  # noqa

    HAS_NOROBOTS = True  # pragma: no cover
except ImportError:
    pass


def captcha_vocabulary(context):
    """Vocabulary with all available captcha implementations."""
    terms = []
    terms.append(SimpleTerm(value="disabled", token="disabled", title=_("Disabled")))

    if HAS_CAPTCHA:  # pragma: no cover
        terms.append(SimpleTerm(value="captcha", token="captcha", title="Captcha"))

    if HAS_RECAPTCHA:  # pragma: no cover
        terms.append(
            SimpleTerm(value="recaptcha", token="recaptcha", title="ReCaptcha")
        )

    if HAS_HCAPTCHA:  # pragma: no cover
        terms.append(SimpleTerm(value="hcaptcha", token="hcaptcha", title="HCaptcha"))

    if HAS_AKISMET:  # pragma: no cover
        terms.append(SimpleTerm(value="akismet", token="akismet", title="Akismet"))

    if HAS_NOROBOTS:  # pragma: no cover
        terms.append(SimpleTerm(value="norobots", token="norobots", title="Norobots"))

    return SimpleVocabulary(terms)


def text_transform_vocabulary(context):
    """Vocabulary with all available portal_transform transformations."""
    terms = []
    terms.append(SimpleTerm(value="text/plain", token="text/plain", title="Plain text"))
    terms.append(SimpleTerm(value="text/html", token="text/html", title="HTML"))
    terms.append(
        SimpleTerm(
            value="text/x-web-markdown", token="text/x-web-markdown", title="Markdown"
        )
    )
    terms.append(
        SimpleTerm(
            value="text/x-web-intelligent",
            token="text/x-web-intelligent",
            title="Intelligent text",
        )
    )
    return SimpleVocabulary(terms)


def ban_type_vocabulary(context):
    """Vocabulary for ban types."""
    terms = [
        SimpleTerm(
            value=BAN_TYPE_COOLDOWN, token=BAN_TYPE_COOLDOWN, title=_("Cooldown")
        ),
        SimpleTerm(value=BAN_TYPE_SHADOW, token=BAN_TYPE_SHADOW, title=_("Shadow")),
        SimpleTerm(
            value=BAN_TYPE_PERMANENT, token=BAN_TYPE_PERMANENT, title=_("Permanent")
        ),
    ]
    return SimpleVocabulary(terms)
