from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

ptc.setupPloneSite()

class Layer(collective.testcaselayer.ptc.BasePTCLayer):
    """Install collective.flowplayer"""

    def afterSetUp(self):
        self.addProfile('plone.app.discussion:default')

DiscussionLayer = Layer([collective.testcaselayer.ptc.ptc_layer])