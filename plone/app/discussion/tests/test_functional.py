import doctest
import unittest2 as unittest
import pprint
import interlude

from plone.testing import layered

from plone.app.discussion.testing import \
    PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE)
normal_testfiles = [
    'functional.txt',
]

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(test ,
                                     optionflags=optionflags,
                                     globs={'interact': interlude.interact,
                                            'pprint': pprint.pprint,
                                            }
                                     ),
                layer=PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING)
        for test in normal_testfiles])
    return suite
