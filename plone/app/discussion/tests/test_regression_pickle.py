# -*- coding: utf-8 -*-
import unittest
import time
from datetime import datetime

from AccessControl import Unauthorized
        
from zope.component import createObject, queryUtility

from OFS.Image import Image

from zope.interface import alsoProvides
from zope.publisher.browser import TestRequest
from zope.annotation.interfaces import IAttributeAnnotatable
from z3c.form.interfaces import IFormLayer

from zope.component import provideAdapter
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.interface import Interface
from zope.component import getMultiAdapter

from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.tests import dummy

from Products.Five.testbrowser import Browser

from Products.PloneTestCase.ptc import PloneTestCase
from Products.PloneTestCase.ptc import FunctionalTestCase
from Products.PloneTestCase.setup import portal_owner, default_password

from plone.app.discussion.browser.comments import CommentsViewlet
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.interfaces import IConversation 
from plone.app.discussion.tests.layer import DiscussionLayer


class TestPostCommentsRegression(FunctionalTestCase):

    layer = DiscussionLayer
    
    def testCantPickleObjectsInAcquisitionWrapper(self):
        """https://dev.plone.org/plone/ticket/11157
        """

        browser = Browser()
        portal_url = self.portal.absolute_url()
        browser.handleErrors = False
        browser.open(portal_url + '/login_form')
        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()
        browser.open(portal_url)
        browser.getLink(id='document').click()
        browser.getControl(name='title').value = "Doc1"
        browser.getControl(name='allowDiscussion:boolean').value = True
        browser.getControl(name='form.button.save').click()
        browser.getLink('Publish').click()
        urldoc1 = browser.url

        # Enable anonymous comment
        browser.open(portal_url+'/@@discussion-settings')
        browser.getControl(name='form.widgets.anonymous_comments:list').value = [True]
        browser.getControl(name='form.buttons.save').click()

        def post(poster=None, password=None, url=urldoc1):
            if poster:
                browser.open(portal_url + '/logout')
                browser.open(portal_url + '/login_form')
                browser.getControl(name='__ac_name').value = poster
                browser.getControl(name='__ac_password').value = password
                browser.getControl(name='submit').click()
            browser.open(url)
            browser.getControl(name='form.widgets.title').value = "%s My Comment" % poster
            browser.getControl(name='form.widgets.text').value = "%s Lorem ipsum" % poster
            submit = browser.getControl(name='form.buttons.comment')
            submit.click()
            browser.open(portal_url + '/logout')

        # Login and post comment as Anonymous
        post()

        browser.open(portal_url + '/login_form')
        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()
        
        browser.open(portal_url + '/doc1/edit')
        browser.getControl(name='title').value = "New Doc1"
        browser.getControl(name='text').value = "Lorem ipsum"
        browser.getControl(name='form.button.save').click()
        
        self.failUnless('Lorem ipsum' in browser.contents)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
