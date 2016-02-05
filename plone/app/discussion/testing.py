# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.robotframework.testing import REMOTE_LIBRARY_ROBOT_TESTING
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.configuration import xmlconfig


try:
    import plone.app.collection  # noqa
    COLLECTION_TYPE = 'Collection'
except ImportError:
    COLLECTION_TYPE = 'Topic'


class PloneAppDiscussion(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    USER_NAME = 'johndoe'
    USER_PASSWORD = 'secret'
    MEMBER_NAME = 'janedoe'
    MEMBER_PASSWORD = 'secret'
    USER_WITH_FULLNAME_NAME = 'jim'
    USER_WITH_FULLNAME_FULLNAME = 'Jim Fulton'
    USER_WITH_FULLNAME_PASSWORD = 'secret'
    MANAGER_USER_NAME = 'manager'
    MANAGER_USER_PASSWORD = 'secret'
    REVIEWER_NAME = 'reviewer'
    REVIEWER_PASSWORD = 'secret'

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.discussion
        xmlconfig.file('configure.zcml',
                       plone.app.discussion,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.discussion:default')

        # Creates some users
        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser(
            self.USER_NAME,
            self.USER_PASSWORD,
            [],
            [],
        )
        acl_users.userFolderAddUser(
            self.MEMBER_NAME,
            self.MEMBER_PASSWORD,
            ['Member'],
            [],
        )
        acl_users.userFolderAddUser(
            self.USER_WITH_FULLNAME_NAME,
            self.USER_WITH_FULLNAME_PASSWORD,
            ['Member'],
            [],
        )
        acl_users.userFolderAddUser(
            self.REVIEWER_NAME,
            self.REVIEWER_PASSWORD,
            ['Member'],
            [],
        )
        mtool = getToolByName(portal, 'portal_membership', None)
        gtool = getToolByName(portal, 'portal_groups', None)
        gtool.addPrincipalToGroup(self.REVIEWER_NAME, 'Reviewers')
        mtool.addMember('jim', 'Jim', ['Member'], [])
        mtool.getMemberById('jim').setMemberProperties(
            {'fullname': 'Jim Fult\xc3\xb8rn'})

        acl_users.userFolderAddUser(
            self.MANAGER_USER_NAME,
            self.MANAGER_USER_PASSWORD,
            ['Manager'],
            [],
        )

        # Add a document
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory(
            id='doc1',
            title='Document 1',
            type_name='Document'
        )


class PloneAppDiscussionRobot(PloneAppDiscussion):

    def setUpPloneSite(self, portal):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True


PLONE_APP_DISCUSSION_ROBOT_FIXTURE = PloneAppDiscussionRobot()
PLONE_APP_DISCUSSION_FIXTURE = PloneAppDiscussion()
PLONE_APP_DISCUSSION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_DISCUSSION_FIXTURE,),
    name='PloneAppDiscussion:Integration')
PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_DISCUSSION_FIXTURE,),
    name='PloneAppDiscussion:Functional')
PLONE_APP_DISCUSSION_ROBOT_TESTING = FunctionalTesting(
    bases=(
        PLONE_APP_DISCUSSION_ROBOT_FIXTURE,
        REMOTE_LIBRARY_ROBOT_TESTING
    ),
    name='PloneAppDiscussion:Robot'
)
