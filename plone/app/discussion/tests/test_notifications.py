import unittest

from email import message_from_string

from Acquisition import aq_base

from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.interfaces import IObjectAddedEvent

from zope.component import createObject
from zope.component import getSiteManager
from zope.component import queryUtility

from Products.PloneTestCase.ptc import PloneTestCase

from Products.MailHost.interfaces import IMailHost
from Products.CMFPlone.tests.utils import MockMailHost

from plone.registry.interfaces import IRegistry

from plone.app.discussion.comment import notify_user
from plone.app.discussion.interfaces import IComment, IConversation, IReplies
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.tests.layer import DiscussionLayer


#class TestUserNotificationUnit(PloneTestCase):
#
#    layer = DiscussionLayer
#
#    def afterSetUp(self):
#        # Set up a mock mailhost
#        self.portal._original_MailHost = self.portal.MailHost
#        self.portal.MailHost = mailhost = MockMailHost('MailHost')
#        sm = getSiteManager(context=self.portal)
#        sm.unregisterUtility(provided=IMailHost)
#        sm.registerUtility(mailhost, provided=IMailHost)
#
#        # We need to fake a valid mail setup
#        self.portal.email_from_address = "portal@plone.test"
#        self.mailhost = self.portal.MailHost
#
#        # Enable user notification setting
#        registry = queryUtility(IRegistry)
#        settings = registry.forInterface(IDiscussionSettings)
#        registry['plone.app.discussion.interfaces.IDiscussionSettings.user_notification_enabled'] = True
#
#        # Create test content
#        self.loginAsPortalOwner()
#        self.portal.invokeFactory('Document', 'doc1')
#        self.portal_discussion = self.portal.portal_discussion
#        self.conversation = IConversation(self.portal.doc1)
#
#    def beforeTearDown(self):
#        self.portal.MailHost = self.portal._original_MailHost
#        sm = getSiteManager(context=self.portal)
#        sm.unregisterUtility(provided=IMailHost)
#        sm.registerUtility(aq_base(self.portal._original_MailHost), provided=IMailHost)
#    
#    def test_notify_user(self):
#        # Add a comment with user notification enabled. Add another comment
#        # and make sure an email is send to the user of the first comment.
#        comment = createObject('plone.Comment')
#        comment.title = 'Comment 1'
#        comment.text = 'Comment text'
#        comment.author_notification = True
#        comment.author_email = "john@plone.test"
#        self.conversation.addComment(comment)
#
#        comment = createObject('plone.Comment')
#        comment.title = 'Comment 2'
#        comment.text = 'Comment text'
#        self.conversation.addComment(comment)
#        
#        self.assertEquals(len(self.mailhost.messages), 1)
#        self.failUnless(self.mailhost.messages[0])
#        msg = self.mailhost.messages[0]
#        self.failUnless('To: john@plone.test' in msg)
#        self.failUnless('From: portal@plone.test' in msg)
#
#        #We expect the headers to be properly header encoded (7-bit):
#        #>>> 'Subject: =?utf-8?q?Some_t=C3=A4st_subject=2E?=' in msg
#        #True

#        #The output should be encoded in a reasonable manner (in this case quoted-printable):
#        #>>> msg
#        #'...Another t=C3=A4st message...You are receiving this mail because T=C3=A4st user\ntest@plone.test...is sending feedback about the site you administer at...
#
#    def test_do_not_notify_user_when_notification_is_disabled(self):
#        # Disable user notification and make sure no email is send to the user.
#        registry = queryUtility(IRegistry)
#        settings = registry.forInterface(IDiscussionSettings)
#        registry['plone.app.discussion.interfaces.IDiscussionSettings.user_notification_enabled'] = False
#
#        comment = createObject('plone.Comment')
#        comment.title = 'Comment 1'
#        comment.text = 'Comment text'
#        comment.author_notification = True
#        comment.author_email = "john@plone.test"
#        self.conversation.addComment(comment)
#
#        comment = createObject('plone.Comment')
#        comment.title = 'Comment 2'
#        comment.text = 'Comment text'
#        self.conversation.addComment(comment)
#        
#        self.assertEquals(len(self.mailhost.messages), 0)
#            
#    def test_do_not_notify_user_when_email_address_is_given(self):
#        comment = createObject('plone.Comment')
#        comment.title = 'Comment 1'
#        comment.text = 'Comment text'
#        comment.author_notification = True
#        self.conversation.addComment(comment)
#
#        comment = createObject('plone.Comment')
#        comment.title = 'Comment 2'
#        comment.text = 'Comment text'
#        self.conversation.addComment(comment)
#        
#        self.assertEquals(len(self.mailhost.messages), 0)
#
#    def test_do_not_notify_user_when_no_sender_is_available(self):
#        # Set sender mail address to nonw and make sure no email is send to the
#        # moderator.
#        self.portal.email_from_address = None
#
#        comment = createObject('plone.Comment')
#        comment.title = 'Comment 1'
#        comment.text = 'Comment text'
#        comment.author_notification = True
#        comment.author_email = "john@plone.test"
#        self.conversation.addComment(comment)
#
#        comment = createObject('plone.Comment')
#        comment.title = 'Comment 2'
#        comment.text = 'Comment text'
#        self.conversation.addComment(comment)
#        
#        self.assertEquals(len(self.mailhost.messages), 0)

class TestModeratorNotificationUnit(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
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
        settings = registry.forInterface(IDiscussionSettings)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.moderator_notification_enabled'] = True        

        # Create test content
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Document', 'doc1')
        self.portal_discussion = self.portal.portal_discussion
        self.conversation = IConversation(self.portal.doc1)

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost), provided=IMailHost)
    
    def test_notify_moderator(self):
        # Add a comment and make sure an email is send to the moderator.
        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        self.conversation.addComment(comment)

        self.assertEquals(len(self.mailhost.messages), 1)
        self.failUnless(self.mailhost.messages[0])
        msg = self.mailhost.messages[0]
        
        if not isinstance(msg, str):
            # Plone 3
            self.failUnless('portal@plone.test' in msg.mfrom)
            self.failUnless('portal@plone.test' in msg.mto)
        else:
            #Plone 4
            self.failUnless('To: portal@plone.test' in msg)
            self.failUnless('From: portal@plone.test' in msg)        

        #We expect the headers to be properly header encoded (7-bit):
        #>>> 'Subject: =?utf-8?q?Some_t=C3=A4st_subject=2E?=' in msg
        #True

        #The output should be encoded in a reasonable manner (in this case quoted-printable):
        #>>> msg
        #'...Another t=C3=A4st message...You are receiving this mail because T=C3=A4st user\ntest@plone.test...is sending feedback about the site you administer at...

    def test_do_not_notify_moderator_when_no_sender_is_available(self):
        # Set sender mail address to nonw and make sure no email is send to the
        # moderator.
        self.portal.email_from_address = None

        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        self.conversation.addComment(comment)
        self.assertEquals(len(self.mailhost.messages), 0)
        
    def test_do_not_notify_moderator_when_notification_is_disabled(self):
        # Disable moderator notification setting and make sure no email is send 
        # to the moderator.
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.moderator_notification_enabled'] = False        

        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        self.conversation.addComment(comment)
        self.assertEquals(len(self.mailhost.messages), 0)

    def test_do_not_notify_moderator_when_moderation_workflow_is_disabled(self):
        # Disable comment moderation and make sure no email is send to the
        # moderator.
        self.portal.portal_types['Document'].allow_discussion = True
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',),
            ('simple_publication_workflow',))
 
        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        self.conversation.addComment(comment)
        self.assertEquals(len(self.mailhost.messages), 0)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
