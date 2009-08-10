from persistent import Persistent

from z3c.form.field import Fields

from zope import interface, schema

from zope.annotation import factory
from zope.annotation.attribute import AttributeAnnotations

from zope.component import adapts, provideAdapter

from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.interface import Interface, implements

from plone.z3cform.fieldsets import extensible
from plone.z3cform.fieldsets.interfaces import IFormExtender

from plone.app.discussion.comment import Comment
from plone.app.discussion.browser.comments import CommentForm

class ICaptcha(Interface):
    captcha = schema.TextLine(title=u"Type the word 'human' in all capital letters.",
                              required=False)

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

    def update(self):
        # Add all fields from the captcha interface
        self.add(ICaptcha, prefix="extra")