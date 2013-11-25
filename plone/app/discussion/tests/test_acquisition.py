# -*- coding: utf-8 -*-
from AccessControl.User import User  # before SpecialUsers
from AccessControl.SpecialUsers import nobody as user_nobody
from AccessControl.PermissionRole import rolesForPermissionOn
from Acquisition import aq_chain, aq_base
from plone.app.discussion.testing import \
    PLONE_APP_DISCUSSION_INTEGRATION_TESTING
from plone.app.discussion.interfaces import IConversation
from plone.app.testing import TEST_USER_ID, setRoles
from Products.CMFCore.utils import getToolByName
from zope.component import createObject

import unittest2 as unittest


dexterity_type_name = 'sample_content_type'
dexterity_object_id = 'instance-of-dexterity-type'
archetypes_object_id = 'instance-of-archetypes-type'
one_state_workflow = 'one_state_workflow'
comment_workflow_acquired_view = 'comment_workflow_acquired_view'

class AcquisitionTest(unittest.TestCase):
    """ Define the expected behaviour of wrapped and unwrapped comments. """

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
        dx_comment = createObject('plone.Comment')
        dx_conversation.addComment(dx_comment)
        self.unwrapped_dexterity_comment = dx_comment
        self.wrapped_dexterity_comment = dx_conversation[dx_comment.id]

        # Create an Archetypes item and add a comment.
        self.portal.invokeFactory(
            id=archetypes_object_id,
            title='Instance Of Archetypes Type',
            type_name='Document',
        )
        
        self.archetypes_object = self.portal.get(archetypes_object_id)
        at_conversation = IConversation(self.archetypes_object)
        self.archetypes_conversation = at_conversation
        at_comment = createObject('plone.Comment')
        at_conversation.addComment(at_comment)
        self.unwrapped_archetypes_comment = at_comment
        self.wrapped_archetypes_comment = at_conversation[at_comment.id]
        

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
            self.wftool.getChainFor(self.unwrapped_archetypes_comment),
            (comment_workflow_acquired_view,)
        )
        self.assertEqual(
            self.wftool.getChainFor(self.unwrapped_dexterity_comment),
            (comment_workflow_acquired_view,)
        )

    def test_comment_acquisition_chain(self):
        """ Test that the acquisition chains for wrapped and unwrapped
            comments are as expected. """
        
        # Unwrapped comments rely on __parent__ attributes to determine 
        # parentage.  Frustratingly there is no guarantee that __parent__
        # is always set, so the computed acquisition chain may be short.
        # In this case the unwrapped AT and DX objects stored as the 
        # conversation parents don't have a __parent__, preventing the portal
        # from being included in the chain.
        self.assertNotIn(self.portal,
                         aq_chain(self.unwrapped_archetypes_comment))
        self.assertNotIn(self.portal,
                         aq_chain(self.unwrapped_dexterity_comment))

        # Wrapped comments however have a complete chain and thus can find the
        # portal object reliably.
        self.assertIn(self.portal,aq_chain(self.wrapped_archetypes_comment))
        self.assertIn(self.portal,aq_chain(self.wrapped_dexterity_comment))

    
    def test_acquiring_comment_permissions(self):
        """ Unwrapped comments should not be able to acquire permissions
            controlled by unreachable objects """
        
        # We use the "Allow sendto" permission as by default it is
        # controlled by the portal, which is unreachable via __parent__
        # attributes on the comments.
        permission = "Allow sendto"

        # Unwrapped comments can't find the portal so just return manager
        self.assertNotIn("Anonymous",
             rolesForPermissionOn(permission,
                                  self.unwrapped_archetypes_comment))
        self.assertNotIn("Anonymous",
             rolesForPermissionOn(permission,
                                  self.unwrapped_dexterity_comment))
        
        # Wrapped objects can find the portal and correctly return the
        # anonymous role.
        self.assertIn("Anonymous",
             rolesForPermissionOn(permission,
                                  self.wrapped_archetypes_comment))
        self.assertIn("Anonymous",
             rolesForPermissionOn(permission,
                                  self.wrapped_dexterity_comment))
    
    def test_acquiring_comment_permissions_via_user_nobody(self):
        """ The current implementation uses user_nobody.has_permission to
            check whether anonymous can view comments.  This confirms it also
            works. """        
        
        # Again we want to use a permission that's not managed by any of our
        # content objects so it must be acquired from the portal.
        permission = "Allow sendto"
    
        self.assertFalse(
             user_nobody.has_permission(permission,
                                        self.unwrapped_archetypes_comment))
        
        self.assertFalse(
             user_nobody.has_permission(permission,
                                        self.unwrapped_dexterity_comment))

        self.assertTrue(
             user_nobody.has_permission(permission,
                                        self.wrapped_archetypes_comment))

        self.assertTrue(
             user_nobody.has_permission(permission,
                                        self.wrapped_dexterity_comment))

class AcquiredPermissionTest(unittest.TestCase):
    """ Test methods of a conversation which rely on acquired permissions """

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.wftool = getToolByName(self.portal, 'portal_workflow')

        # Disable workflow for comments and content.
        self.wftool.setChainForPortalTypes(["Discussion Item"],[])
        self.wftool.setChainForPortalTypes([dexterity_type_name],[])

        # Create a dexterity item.
        self.portal.invokeFactory(
            id=dexterity_object_id,
            title='Instance Of Dexterity Type',
            type_name=dexterity_type_name,
        )
        
        self.content = self.portal.get(dexterity_object_id)

        # Absolutely make sure that we're replicating the case of an 
        # incomplete chain correctly.
        aq_base(self.content).__parent__ = None
        
        self.conversation = IConversation(self.content)
        
        # Add a comment
        comment = createObject('plone.Comment')
        self.conversation.addComment(comment)
        self.comment = comment
    
    def test_view_permission_is_only_available_on_portal(self):
        """ Check that the test setup is correct """
        
        content_roles = rolesForPermissionOn("View",aq_base(self.content))
        self.assertNotIn("Anonymous",content_roles)
        
        comment_roles = rolesForPermissionOn("View",aq_base(self.comment))
        self.assertNotIn("Anonymous",comment_roles)
        
        # This actually acquires view from the app root, but we don't really
        # care, we just need to confirm that something above our content
        # object will give us View.
        portal_roles = rolesForPermissionOn("View",self.portal)
        self.assertIn("Anonymous",portal_roles)

    # The following tests fail when the conversation uses unwrapped comment
    # objects to determine whether an anonymous user has the view permission.
        
    def test_total_comments(self):
        self.assertEqual(self.conversation.total_comments,1)
    
    def test_last_comment_date(self):
        self.assertEqual(self.conversation.last_comment_date,
                         self.comment.creation_date)
    
    def test_public_commentators(self):
        self.assertEqual(self.conversation.public_commentators,
                         (self.comment.author_username,))



def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
