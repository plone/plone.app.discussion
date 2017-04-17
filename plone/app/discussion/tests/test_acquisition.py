# -*- coding: utf-8 -*-
from AccessControl.User import User  # before SpecialUsers
from AccessControl.SpecialUsers import nobody as user_nobody
from Acquisition import aq_chain
from plone.app.discussion.testing import \
    PLONE_APP_DISCUSSION_INTEGRATION_TESTING
from plone.app.discussion.interfaces import IConversation
from plone.app.testing import TEST_USER_ID, setRoles
from Products.CMFCore.utils import getToolByName
from zope.component import createObject

import unittest2 as unittest


User = User  # stop pyflakes from complaining about side effect import

dexterity_type_name = 'sample_content_type'
dexterity_object_id = 'instance-of-dexterity-type'
archetypes_object_id = 'instance-of-archetypes-type'
one_state_workflow = 'one_state_workflow'
comment_workflow_acquired_view = 'comment_workflow_acquired_view'


def _anonymousCanView(obj):
    """Use rolesOfPermission() to sees if Anonymous has View permission on an
    object"""
    roles_of_view_permission = obj.rolesOfPermission("View")
    # rolesOfPermission returns a list of dictionaries that have the key
    # 'name' for role.
    anon_views = [r for r in roles_of_view_permission
                  if r['name'] == 'Anonymous']
    # only one entry per role should be present
    anon_view = anon_views[0]
    # if this role has the permission, 'selected' is set to 'SELECTED'
    return anon_view['selected'] == 'SELECTED'


class DexterityAcquisitionTest(unittest.TestCase):
    """See test_view_permission."""

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.wftool = getToolByName(self.portal, 'portal_workflow')

        # Use customized workflow for comments.
        self.wftool.setChainForPortalTypes(
            ['Discussion Item'],
            (comment_workflow_acquired_view,),
        )

        # Use one_state_workflow for Document and sample_content_type,
        # so they're always published.
        self.wftool.setChainForPortalTypes(
            ['Document', dexterity_type_name],
            (one_state_workflow,),
        )

        # Create a dexterity item and add a comment.
        self.portal.invokeFactory(
            id=dexterity_object_id,
            title='Instance Of Dexterity Type',
            type_name=dexterity_type_name,
        )
        self.dexterity_object = self.portal.get(dexterity_object_id)
        dx_conversation = IConversation(self.dexterity_object)
        self.dexterity_conversation = dx_conversation
        comment1 = createObject('plone.Comment')
        dx_conversation.addComment(comment1)
        self.dexterity_comment = comment1

        # Create an Archetypes item and add a comment.
        self.portal.invokeFactory(
            id=archetypes_object_id,
            title='Instance Of Archetypes Type',
            type_name='Document',
        )
        self.archetypes_object = self.portal.get(archetypes_object_id)
        at_conversation = IConversation(self.archetypes_object)
        self.archetypes_conversation = at_conversation
        comment2 = createObject('plone.Comment')
        at_conversation.addComment(comment2)
        self.archetypes_comment = comment2

    def test_workflows_installed(self):
        """Check that the new comment workflow has been installed properly.
        (Just a test to check our test setup.)
        """
        workflows = self.wftool.objectIds()
        self.assertTrue('comment_workflow_acquired_view' in workflows)

    def test_workflows_applied(self):
        """Check that all objects have the workflow that we expect.
        (Just a test to check our test setup.)"""
        self.assertEqual(
            self.wftool.getChainFor(self.archetypes_object),
            (one_state_workflow,)
        )
        self.assertEqual(
            self.wftool.getChainFor(self.dexterity_object),
            (one_state_workflow,)
        )
        self.assertEqual(
            self.wftool.getChainFor(self.archetypes_comment),
            (comment_workflow_acquired_view,)
        )
        self.assertEqual(
            self.wftool.getChainFor(self.dexterity_comment),
            (comment_workflow_acquired_view,)
        )

    def test_view_permission(self):
        """Test that if the View permission on Discussion Items is acquired,
        Anonymous can view comments on published items."""

        # Anonymous has View permission on commented objects.
        self.assertTrue(_anonymousCanView(self.archetypes_object))
        self.assertTrue(_anonymousCanView(self.dexterity_object))
        self.assertTrue(
            user_nobody.has_permission("View", self.archetypes_object))
        self.assertTrue(
            user_nobody.has_permission("View", self.dexterity_object))

        # Anonymous also passes the user_nobody.has_permission() test
        # on comments.
        self.assertTrue(
            user_nobody.has_permission("View", self.archetypes_comment))
        self.assertTrue(
            user_nobody.has_permission("View", self.dexterity_comment))

        # Fails: Anonymous should therefore have View permission on the
        # comments when we use rolesOfPermission.
        self.assertTrue(_anonymousCanView(self.archetypes_comment))
        self.assertTrue(_anonymousCanView(self.dexterity_comment))

    def test_acquisition_chain(self):
        """The acquisition chain for the comment should contain the same items
        as that of the conversation.

        Note that the list returned by aq_inner has the innermost object
        first."""

        # Fails: list index out of range
        at_comment_chain = aq_chain(self.archetypes_comment)
        at_conversation_chain = aq_chain(self.archetypes_conversation)
        for (index, item) in enumerate(at_conversation_chain):
            self.assertEqual(item, at_comment_chain[index + 1])

        # Fails: list index out of range
        dx_comment_chain = aq_chain(self.dexterity_comment)
        dx_conversation_chain = aq_chain(self.dexterity_conversation)
        for (index, item) in enumerate(dx_conversation_chain):
            self.assertEqual(item, dx_comment_chain[index + 1])


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
