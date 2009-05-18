import unittest

from Products.PloneTestCase.ptc import PloneTestCase
from plone.app.discussion.tests.layer import DiscussionLayer

class TestIndexers(PloneTestCase):
    
    layer = DiscussionLayer
    
    def test_title(self):
        pass

    def test_description(self):
        pass
    
    def test_dates(self):
        # created, modified, effective etc
        pass

    def test_searchable_text(self):
        pass

    def test_creator(self):
        pass

    def test_title(self):
        pass
        
    def test_in_reply_to(self):
        pass
    
    def test_path(self):
        pass
    
    def test_review_state(self):
        pass
    
    def test_object_provides(self):
        pass
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)