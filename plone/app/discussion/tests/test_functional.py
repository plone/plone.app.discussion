# -*- coding: utf-8 -*-
"""Functional Doctests for plone.app.discussion.

   These test are only triggered when Plone 4 (and plone.testing) is installed.
"""
import doctest

import unittest2 as unittest
import pprint

from plone.testing import layered

from plone.app.discussion.testing import \
    PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING


optionflags = (
    doctest.ELLIPSIS | \
    doctest.NORMALIZE_WHITESPACE | \
    doctest.REPORT_ONLY_FIRST_FAILURE)
normal_testfiles = [
    'functional_test_comments.txt',
    'functional_test_comment_review_workflow.txt',
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(test,
                                     optionflags=optionflags,
                                     globs={'pprint': pprint.pprint,
                                            }
                                     ),
                layer=PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING)
        for test in normal_testfiles])
    return suite
