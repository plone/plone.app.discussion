"""Functional Doctests for plone.app.discussion.
"""

from ..testing import PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING
from plone.testing import layered

import doctest
import pprint
import unittest


optionflags = (
    doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
)
normal_testfiles = [
    "functional_test_comments.rst",
    "functional_test_comment_review_workflow.txt",
    "functional_test_behavior_discussion.rst",
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            layered(
                doctest.DocFileSuite(
                    test,
                    optionflags=optionflags,
                    globs={
                        "pprint": pprint.pprint,
                    },
                ),
                layer=PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING,
            )
            for test in normal_testfiles
        ]
    )
    return suite
