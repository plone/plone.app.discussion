from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import ptc
from Products.PloneTestCase import layer
from Products.Five import zcml
from Products.Five import fiveconfigure

ptc.setupPloneSite(
    extension_profiles=('plone.app.discussion:default', )
)

class DiscussionLayer(layer.PloneSite):
    """Configure plone.app.discussion"""

    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        import plone.app.discussion
        zcml.load_config("configure.zcml", plone.app.discussion)
        fiveconfigure.debug_mode = False
        ztc.installPackage("plone.app.discussion", quiet=1)

    @classmethod
    def tearDown(cls):
        pass
