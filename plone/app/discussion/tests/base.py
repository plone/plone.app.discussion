import unittest

from zope.testing import doctestunit
from zope.component import testing, getMultiAdapter
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserView
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite(extension_profiles=['plone.app.discussion:default'])

import plone.app.discussion

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             plone.app.discussion)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

