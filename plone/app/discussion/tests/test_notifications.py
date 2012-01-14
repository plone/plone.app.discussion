# -*- coding: utf-8 -*-

import unittest2 as unittest

from Acquisition import aq_base

from zope.component import createObject
from zope.component import getSiteManager
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID, setRoles

from Products.MailHost.interfaces import IMailHost
from Products.CMFPlone.tests.utils import MockMailHost

from plone.registry.interfaces import IRegistry

from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.testing import\
    PLONE_APP_DISCUSSION_INTEGRATION_TESTING


class TestUserNotificationUnit(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # We need to fake a valid mail setup
        self.portal.email_from_address = "portal@plone.test"
        self.mailhost = self.portal.MailHost
        # Enable user notification setting
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings' +
                 '.user_notification_enabled'] = True
        # Create test content
        self.portal.invokeFactory('Document', 'doc1')
        self.portal_discussion = self.portal.portal_discussion
        # Archetypes content types store data as utf-8 encoded strings
        # The missing u in front of a string is therefor not missing
        self.portal.doc1.title = 'Kölle Alaaf'  # What is "Fasching"?
        self.conversation = IConversation(self.portal.doc1)

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)

    def test_notify_user(self):
        # Add a comment with user notification enabled. Add another comment
        # and make sure an email is send to the user of the first comment.
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        comment.author_email = "john@plone.test"
        self.conversation.addComment(comment)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        comment_id = self.conversation.addComment(comment)

        self.assertEqual(len(self.mailhost.messages), 1)
        self.assertTrue(self.mailhost.messages[0])
        msg = str(self.mailhost.messages[0])
        self.assertTrue('To: john@plone.test' in msg)
        self.assertTrue('From: portal@plone.test' in msg)
        # We expect the headers to be properly header encoded (7-bit):
        self.assertTrue(
            'Subject: =?utf-8?q?A_comment_has_been_posted=2E?=\n'
            in msg)
        # The output should be encoded in a reasonable manner
        # (in this case quoted-printable):
        self.assertTrue(
            "A comment on \'K=C3=B6lle Alaaf\' has been posted here:"
            in msg)
        self.assertTrue(
            "http://nohost/plone/d=\noc1/view#%s"
            % comment_id
            in msg)
        self.assertTrue('Comment text' in msg)
        self.assertFalse('Approve comment' in msg)
        self.assertFalse('Delete comment' in msg)

    def test_do_not_notify_user_when_notification_is_disabled(self):
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.' +
                  'user_notification_enabled'] = False
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        comment.author_email = "john@plone.test"
        self.conversation.addComment(comment)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        self.conversation.addComment(comment)

        self.assertEqual(len(self.mailhost.messages), 0)

    def test_do_not_notify_user_when_email_address_is_given(self):
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        self.conversation.addComment(comment)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        self.conversation.addComment(comment)

        self.assertEqual(len(self.mailhost.messages), 0)

    def test_do_not_notify_user_when_no_sender_is_available(self):
        # Set sender mail address to none and make sure no email is send to
        # the moderator.
        self.portal.email_from_address = None
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        comment.author_email = "john@plone.test"
        self.conversation.addComment(comment)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        self.conversation.addComment(comment)

        self.assertEqual(len(self.mailhost.messages), 0)

    def test_notify_only_once(self):
        # When a user has added two comments in a conversation and has
        # both times requested email notification, do not send him two
        # emails when another comment has been added.
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        comment.author_email = "john@plone.test"
        self.conversation.addComment(comment)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        comment.author_email = "john@plone.test"

        self.conversation.addComment(comment)

        # Note that we might want to get rid of this message, as the
        # new comment is added by the same user.
        self.assertEqual(len(self.mailhost.messages), 1)
        self.mailhost.reset()
        self.assertEqual(len(self.mailhost.messages), 0)


class TestModeratorNotificationUnit(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # We need to fake a valid mail setup
        self.portal.email_from_address = "portal@plone.test"
        self.mailhost = self.portal.MailHost
        # Enable comment moderation
        self.portal.portal_types['Document'].allow_discussion = True
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',),
            ('comment_review_workflow',))
        # Enable moderator notification setting
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.' +
                'moderator_notification_enabled'] = True
        # Create test content
        self.portal.invokeFactory('Document', 'doc1')
        self.portal_discussion = self.portal.portal_discussion
        # Archetypes content types store data as utf-8 encoded strings
        # The missing u in front of a string is therefor not missing
        self.portal.doc1.title = 'Kölle Alaaf'  # What is "Fasching"?
        self.conversation = IConversation(self.portal.doc1)

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)

    def test_notify_moderator(self):
        # Add a comment and make sure an email is send to the moderator.
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        comment_id = self.conversation.addComment(comment)

        self.assertEqual(len(self.mailhost.messages), 1)
        self.assertTrue(self.mailhost.messages[0])
        msg = self.mailhost.messages[0]
        self.assertTrue('To: portal@plone.test' in msg)
        self.assertTrue('From: portal@plone.test' in msg)
        # We expect the headers to be properly header encoded (7-bit):
        self.assertTrue(
            'Subject: =?utf-8?q?A_comment_has_been_posted=2E?=\n'
            in msg)
        # The output should be encoded in a reasonable manner
        # (in this case quoted-printable):
        self.assertTrue(
            "A comment on \'K=C3=B6lle Alaaf\' has been posted here:"
            in msg)
        self.assertTrue(
            "http://nohost/plone/d=\noc1/view#%s"
            % comment_id
            in msg)
        self.assertTrue('Comment text' in msg)
        self.assertTrue(
            'Approve comment:\nhttp://nohost/plone/doc1/' +
            '++conversation++default/%s/@@moderat=\ne-publish-comment'
            % comment_id in msg)
        self.assertTrue(
            'Delete comment:\nhttp://nohost/plone/doc1/' +
            '++conversation++default/%s/@@moderat=\ne-delete-comment'
            % comment_id in msg)

    def test_notify_moderator_specific_address(self):
        # A moderator email address can be specified in the control panel.
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings' +
                 '.moderator_email'] = 'test@example.com'
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        self.conversation.addComment(comment)

        self.assertEqual(len(self.mailhost.messages), 1)
        msg = self.mailhost.messages[0]
        if not isinstance(msg, str):
            self.assertTrue('test@example.com' in msg.mto)
        else:
            self.assertTrue('To: test@example.com' in msg)

    def test_do_not_notify_moderator_when_no_sender_is_available(self):
        # Set sender mail address to nonw and make sure no email is send to the
        # moderator.
        self.portal.email_from_address = None
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        self.conversation.addComment(comment)

        self.assertEqual(len(self.mailhost.messages), 0)

    def test_do_not_notify_moderator_when_notification_is_disabled(self):
        # Disable moderator notification setting and make sure no email is send
        # to the moderator.
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.' +
                 'moderator_notification_enabled'] = False
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        self.conversation.addComment(comment)

        self.assertEqual(len(self.mailhost.messages), 0)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
