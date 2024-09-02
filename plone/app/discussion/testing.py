from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_ROBOT_TESTING
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName


class PloneAppDiscussion(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    USER_NAME = "johndoe"
    USER_PASSWORD = TEST_USER_PASSWORD
    MEMBER_NAME = "janedoe"
    MEMBER_PASSWORD = TEST_USER_PASSWORD
    USER_WITH_FULLNAME_NAME = "jim"
    USER_WITH_FULLNAME_FULLNAME = "Jim Fulton"
    USER_WITH_FULLNAME_PASSWORD = TEST_USER_PASSWORD
    MANAGER_USER_NAME = "manager"
    MANAGER_USER_PASSWORD = TEST_USER_PASSWORD
    REVIEWER_NAME = "reviewer"
    REVIEWER_PASSWORD = TEST_USER_PASSWORD

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.discussion

        self.loadZCML(
            package=plone.app.discussion,
            context=configurationContext,
        )

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, "plone.app.discussion:default")

        # Creates some users
        acl_users = getToolByName(portal, "acl_users")
        acl_users.userFolderAddUser(
            self.USER_NAME,
            self.USER_PASSWORD,
            [],
            [],
        )
        acl_users.userFolderAddUser(
            self.MEMBER_NAME,
            self.MEMBER_PASSWORD,
            ["Member"],
            [],
        )
        acl_users.userFolderAddUser(
            self.USER_WITH_FULLNAME_NAME,
            self.USER_WITH_FULLNAME_PASSWORD,
            ["Member"],
            [],
        )
        acl_users.userFolderAddUser(
            self.REVIEWER_NAME,
            self.REVIEWER_PASSWORD,
            ["Member"],
            [],
        )
        mtool = getToolByName(portal, "portal_membership", None)
        gtool = getToolByName(portal, "portal_groups", None)
        gtool.addPrincipalToGroup(self.REVIEWER_NAME, "Reviewers")
        mtool.addMember("jim", "Jim", ["Member"], [])
        mtool.getMemberById("jim").setMemberProperties(
            {"fullname": "Jim Fult\xc3\xb8rn"}
        )

        acl_users.userFolderAddUser(
            self.MANAGER_USER_NAME,
            self.MANAGER_USER_PASSWORD,
            ["Manager"],
            [],
        )

        # Add a document
        setRoles(portal, TEST_USER_ID, ["Manager"])
        portal.invokeFactory(
            id="doc1",
            title="Document 1",
            type_name="Document",
        )


class PloneAppDiscussionRobot(PloneAppDiscussion):
    defaultBases = (
        PLONE_APP_CONTENTTYPES_FIXTURE,
        REMOTE_LIBRARY_ROBOT_TESTING,
    )


PLONE_APP_DISCUSSION_ROBOT_FIXTURE = PloneAppDiscussionRobot()
PLONE_APP_DISCUSSION_FIXTURE = PloneAppDiscussion()
PLONE_APP_DISCUSSION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_DISCUSSION_FIXTURE,), name="PloneAppDiscussion:Integration"
)
PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_DISCUSSION_FIXTURE,), name="PloneAppDiscussion:Functional"
)
PLONE_APP_DISCUSSION_ROBOT_TESTING = FunctionalTesting(
    bases=(PLONE_APP_DISCUSSION_ROBOT_FIXTURE,),
    name="PloneAppDiscussion:Robot",
)
