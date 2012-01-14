from Products.CMFCore.utils import getToolByName

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from zope.configuration import xmlconfig


class PloneAppDiscussion(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    USER_NAME = 'johndoe'
    USER_PASSWORD = 'secret'
    MEMBER_NAME = 'janedoe'
    MEMBER_PASSWORD = 'secret'
    USER_WITH_FULLNAME_NAME = 'jim'
    USER_WITH_FULLNAME_FULLNAME = 'Jim Fulton'
    USER_WITH_FULLNAME_PASSWORD = 'secret'
    MANAGER_USER_NAME = 'manager'
    MANAGER_USER_PASSWORD = 'secret'

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
        mtool = getToolByName(portal, 'portal_membership', None)
        mtool.addMember('jim', 'Jim', ['Member'], [])
        mtool.getMemberById('jim').setMemberProperties(
            {"fullname": 'Jim Fult\xc3\xb8rn'})

        acl_users.userFolderAddUser(
            self.MANAGER_USER_NAME,
            self.MANAGER_USER_PASSWORD,
            ['Manager'],
            [],
        )

PLONE_APP_DISCUSSION_FIXTURE = PloneAppDiscussion()
PLONE_APP_DISCUSSION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_DISCUSSION_FIXTURE,),
    name="PloneAppDiscussion:Integration")
PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_DISCUSSION_FIXTURE,),
    name="PloneAppDiscussion:Functional")
