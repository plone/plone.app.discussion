import unittest

from base import TestCase

from zope.testing import doctestunit
from zope.component import testing, getMultiAdapter
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserView
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

class APITest(TestCase):
    def afterSetUp(self):
        # XXX If we make this a layer, it only get run once...
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
            
    def test_test(self):
        raise NotImplementedError
    

def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(APITest),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
