from plone.app.discussion.browser.comment import View
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IReplies
from plone.app.discussion.testing import PLONE_APP_DISCUSSION_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from zope.component import createObject
from zope.component import getMultiAdapter

import datetime
import logging
import unittest


logger = logging.getLogger("plone.app.discussion.tests")
logger.addHandler(logging.StreamHandler())


def normalize(value):
    # Strip all white spaces of every line, then join on one line.
    # But try to avoid getting 'Go to<a href' instead of 'Go to <a href'.
    lines = []
    for line in value.splitlines():
        line = line.strip()
        if (
            line.startswith("<")
            and not line.startswith("</")
            and not line.startswith("<br")
        ):
            line = " " + line
        lines.append(line)
    return "".join(lines).strip()


class CommentTest(unittest.TestCase):
    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        workflow = self.portal.portal_workflow
        workflow.doActionFor(self.portal.doc1, "publish")

        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.catalog = getToolByName(self.portal, "portal_catalog")
        self.document_brain = self.catalog.searchResults(portal_type="Document")[0]

    def test_factory(self):
        comment1 = createObject("plone.Comment")
        self.assertTrue(IComment.providedBy(comment1))

    def test_UTCDates(self):
        utc_to_local_diff = datetime.datetime.now() - datetime.datetime.utcnow()
        utc_to_local_diff = abs(utc_to_local_diff.seconds)
        if utc_to_local_diff < 60:
            logger.warning(
                "Your computer is living in a timezone where local "
                "time equals utc time. Some potential errors can "
                "get hidden by that"
            )
        comment1 = createObject("plone.Comment")
        local_utc = datetime.datetime.now().astimezone(datetime.timezone.utc)
        for date in (comment1.creation_date, comment1.modification_date):
            difference = abs(date - local_utc)
            difference = difference.seconds
            # We hope that between comment1 and local_utc happen less than
            # 10 seconds
            self.assertFalse(difference // 10)

    def test_id(self):
        comment1 = createObject("plone.Comment")
        comment1.comment_id = 123
        self.assertEqual("123", comment1.id)
        self.assertEqual("123", comment1.getId())
        self.assertEqual("123", comment1.__name__)

    def test_uid(self):
        conversation = IConversation(self.portal.doc1)
        comment1 = createObject("plone.Comment")
        conversation.addComment(comment1)
        comment_brain = self.catalog.searchResults(
            portal_type="Discussion Item",
        )[0]
        self.assertTrue(comment_brain.UID)

    def test_uid_is_unique(self):
        conversation = IConversation(self.portal.doc1)
        comment1 = createObject("plone.Comment")
        conversation.addComment(comment1)
        comment2 = createObject("plone.Comment")
        conversation.addComment(comment2)
        brains = self.catalog.searchResults(
            portal_type="Discussion Item",
        )
        self.assertNotEqual(brains[0].UID, brains[1].UID)

    def test_comment_uid_differs_from_content_uid(self):
        conversation = IConversation(self.portal.doc1)
        comment1 = createObject("plone.Comment")
        conversation.addComment(comment1)
        comment_brain = self.catalog.searchResults(
            portal_type="Discussion Item",
        )[0]
        self.assertNotEqual(self.document_brain.UID, comment_brain.UID)

    def test_title(self):
        conversation = IConversation(self.portal.doc1)
        comment1 = createObject("plone.Comment")
        comment1.author_name = "Jim Fulton"
        conversation.addComment(comment1)
        self.assertEqual("Jim Fulton on Document 1", comment1.Title())

    def test_no_name_title(self):
        conversation = IConversation(self.portal.doc1)
        comment1 = createObject("plone.Comment")
        conversation.addComment(comment1)
        self.assertEqual("Anonymous on Document 1", comment1.Title())

    def test_title_special_characters(self):
        self.portal.invokeFactory(
            id="doc_sp_chars",
            title="Document äüö",
            type_name="Document",
        )
        conversation = IConversation(self.portal.doc_sp_chars)
        comment1 = createObject("plone.Comment")
        comment1.author_name = "Tarek Ziadé"
        conversation.addComment(comment1)
        self.assertEqual("Tarek Ziadé on Document äüö", comment1.Title())

    def test_title_special_characters_utf8(self):
        self.portal.invokeFactory(
            id="doc_sp_chars_utf8",
            title="Document ëïû",
            type_name="Document",
        )
        conversation = IConversation(self.portal.doc_sp_chars_utf8)
        comment1 = createObject("plone.Comment")
        comment1.author_name = "Hüüb Bôûmä"
        conversation.addComment(comment1)
        self.assertEqual("Hüüb Bôûmä on Document ëïû", comment1.Title())

    def test_creator(self):
        comment1 = createObject("plone.Comment")
        comment1.creator = "jim"
        self.assertEqual("jim", comment1.Creator())

    def test_creator_author_name(self):
        comment1 = createObject("plone.Comment")
        comment1.author_name = "joey"
        self.assertEqual("joey", comment1.Creator())

    def test_owner(self):
        comment1 = createObject("plone.Comment")
        self.assertEqual(
            (["plone", "acl_users"], TEST_USER_ID), comment1.getOwnerTuple()
        )

    def test_type(self):
        comment1 = createObject("plone.Comment")
        self.assertEqual(comment1.Type(), "Comment")

    def test_mime_type(self):
        comment1 = createObject("plone.Comment")
        self.assertEqual(comment1.mime_type, "text/plain")

    def test_getText(self):
        comment1 = createObject("plone.Comment")
        comment1.text = "First paragraph\n\nSecond_paragraph"
        self.assertEqual(
            normalize(comment1.getText()),
            "<p>First paragraph<br><br>Second_paragraph</p>",
        )

    def test_getText_escapes_HTML(self):
        comment1 = createObject("plone.Comment")
        comment1.text = "<b>Got HTML?</b>"
        self.assertEqual(
            normalize(comment1.getText()),
            "<p>&lt;b&gt;Got HTML?&lt;/b&gt;</p>",
        )

    def test_getText_with_non_ascii_characters(self):
        comment1 = createObject("plone.Comment")
        comment1.text = "Umlaute sind ä, ö und ü."
        out = b"<p>Umlaute sind \xc3\xa4, \xc3\xb6 und \xc3\xbc.</p>"
        self.assertEqual(normalize(comment1.getText()), out.decode("utf8"))

    def test_getText_doesnt_link(self):
        comment1 = createObject("plone.Comment")
        comment1.text = "Go to http://www.plone.org"
        self.assertEqual(
            normalize(comment1.getText()),
            "<p>Go to http://www.plone.org</p>",
        )

    def test_getText_uses_comment_mime_type(self):
        comment1 = createObject("plone.Comment")
        comment1.text = "Go to http://www.plone.org"
        comment1.mime_type = "text/x-web-intelligent"
        self.assertEqual(
            normalize(comment1.getText()),
            'Go to <a href="http://www.plone.org" '
            + 'rel="nofollow">http://www.plone.org</a>',
        )

    def test_getText_uses_comment_mime_type_html(self):
        comment1 = createObject("plone.Comment")
        comment1.text = 'Go to <a href="http://www.plone.org">plone.org</a>'
        comment1.mime_type = "text/html"
        self.assertEqual(
            normalize(comment1.getText()),
            'Go to <a href="http://www.plone.org">plone.org</a>',
        )

    def test_getText_w_custom_targetMimetype(self):
        comment1 = createObject("plone.Comment")
        comment1.text = "para"
        self.assertEqual(comment1.getText(targetMimetype="text/plain"), "para")

    def test_getText_invalid_transformation_raises_error(self):
        conversation = IConversation(self.portal.doc1)
        comment1 = createObject("plone.Comment")
        comment1.mime_type = "text/x-html-safe"
        comment1.text = "para"
        conversation.addComment(comment1)
        self.assertEqual(comment1.getText(targetMimetype="text/html"), "para")

    def test_traversal(self):
        # make sure comments are traversable, have an id, absolute_url and
        # physical path

        conversation = IConversation(self.portal.doc1)

        comment1 = createObject("plone.Comment")
        comment1.text = "Comment text"

        new_comment1_id = conversation.addComment(comment1)

        comment = self.portal.doc1.restrictedTraverse(
            f"++conversation++default/{new_comment1_id}",
        )
        self.assertTrue(IComment.providedBy(comment))

        self.assertEqual(
            (
                "",
                "plone",
                "doc1",
                "++conversation++default",
                str(new_comment1_id),
            ),
            comment.getPhysicalPath(),
        )
        self.assertEqual(
            "http://nohost/plone/doc1/++conversation++default/" + str(new_comment1_id),
            comment.absolute_url(),
        )

    def test_view_blob_types(self):
        """
        Make sure that traversal to images/files redirects to the
        version of the url with a /view in it.
        """
        self.portal.invokeFactory(
            id="image1",
            title="Image",
            type_name="Image",
        )
        conversation = IConversation(self.portal.image1)

        comment1 = createObject("plone.Comment")
        comment1.text = "Comment text"
        new_comment1_id = conversation.addComment(comment1)
        comment = self.portal.image1.restrictedTraverse(
            f"++conversation++default/{new_comment1_id}",
        )

        view = View(comment, self.request)
        View.__call__(view)
        response = self.request.response
        self.assertIn("/view", response.headers["location"])

    def test_workflow(self):
        """Basic test for the 'comment_review_workflow'"""
        self.portal.portal_workflow.setChainForPortalTypes(
            ("Discussion Item",),
            ("comment_review_workflow,"),
        )

        conversation = IConversation(self.portal.doc1)
        comment1 = createObject("plone.Comment")
        new_comment1_id = conversation.addComment(comment1)

        comment = conversation[new_comment1_id]

        # Make sure comments use the 'comment_review_workflow'
        chain = self.portal.portal_workflow.getChainFor(comment)
        self.assertEqual(("comment_review_workflow",), chain)

        # Ensure the initial state was entered and recorded
        self.assertEqual(
            1,
            len(comment.workflow_history["comment_review_workflow"]),
        )
        self.assertEqual(
            None,
            comment.workflow_history["comment_review_workflow"][0]["action"],
        )
        self.assertEqual(
            "pending",
            self.portal.portal_workflow.getInfoFor(comment, "review_state"),
        )

    def test_fti(self):
        # test that we can look up an FTI for Discussion Item

        self.assertIn(
            "Discussion Item",
            self.portal.portal_types.objectIds(),
        )

        comment1 = createObject("plone.Comment")

        fti = self.portal.portal_types.getTypeInfo(comment1)
        self.assertEqual("Discussion Item", fti.getTypeInfo(comment1).getId())

    def test_view(self):
        # make sure that the comment view is there and redirects to the right
        # URL

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Create a comment
        comment1 = createObject("plone.Comment")
        comment1.text = "Comment text"

        # Add comment to the conversation
        new_comment1_id = conversation.addComment(comment1)

        comment = self.portal.doc1.restrictedTraverse(
            f"++conversation++default/{new_comment1_id}",
        )

        # make sure the view is there
        self.assertTrue(
            getMultiAdapter(
                (comment, self.request),
                name="view",
            ),
        )

        # make sure the HTTP redirect (status code 302) works when a comment
        # is called directly
        view = View(comment, self.request)
        View.__call__(view)
        self.assertEqual(self.request.response.status, 302)

    def test_comment_published_for_manager(self):
        # Test that comments posted by a Manager are automatically published.
        # Set the current user to Manager
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # Create a conversation
        conversation = IConversation(self.portal.doc1)

        # Create a comment
        comment = createObject("plone.Comment")
        comment.text = "This is a manager comment"

        # Add the comment to the conversation
        comment_id = conversation.addComment(comment)

        # Get the comment from the conversation
        comment = conversation[comment_id]

        # Assert that the comment's workflow state is 'published'
        review_state = self.portal.portal_workflow.getInfoFor(comment, "review_state")
        self.assertEqual("published", review_state)

    def test_comment_pending_for_new_member(self):
        # Test that comments posted by a newly created Member are in pending state.
        # Create a new user with Member role
        membership = getToolByName(self.portal, "portal_membership")
        membership.addMember("new_member", "password", ["Member"], [])

        # Log in as the new member
        from plone.app.testing import login

        login(self.portal, "new_member")

        # Make sure the comment_review_workflow is set for Discussion Items
        self.portal.portal_workflow.setChainForPortalTypes(
            ("Discussion Item",), ("comment_review_workflow",)
        )

        # Create a conversation
        conversation = IConversation(self.portal.doc1)

        # Create a comment
        comment = createObject("plone.Comment")
        comment.text = "This is a comment from a new member"

        # Add the comment to the conversation
        comment_id = conversation.addComment(comment)

        # Get the comment from the conversation
        comment = conversation[comment_id]

        # Assert that the comment's workflow state is 'pending'
        review_state = self.portal.portal_workflow.getInfoFor(comment, "review_state")
        self.assertEqual("pending", review_state)


class RepliesTest(unittest.TestCase):
    # test the IReplies adapter on a comment

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        workflow = self.portal.portal_workflow
        workflow.doActionFor(self.portal.doc1, "publish")

    def test_add_comment(self):
        # Add comments to a CommentReplies adapter

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Add a comment to the conversation
        replies = IReplies(conversation)

        comment = createObject("plone.Comment")
        comment.text = "Comment text"
        new_id = replies.addComment(comment)
        comment = self.portal.doc1.restrictedTraverse(
            f"++conversation++default/{new_id}",
        )

        # Add a reply to the CommentReplies adapter of the first comment
        re_comment = createObject("plone.Comment")
        re_comment.text = "Comment text"

        replies = IReplies(comment)

        new_re_id = replies.addComment(re_comment)

        # check that replies provides the IReplies interface
        self.assertTrue(IReplies.providedBy(replies))

        # Make sure our comment was added
        self.assertTrue(new_re_id in replies)

        # Make sure it is also reflected in the conversation
        self.assertTrue(new_re_id in conversation)

        # Make sure the conversation has the correct comment id
        self.assertEqual(conversation[new_re_id].comment_id, new_re_id)

    def test_delete_comment(self):
        # Add and remove a comment to a CommentReplies adapter

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Add a comment to the conversation
        replies = IReplies(conversation)

        comment = createObject("plone.Comment")
        comment.text = "Comment text"
        new_id = replies.addComment(comment)
        comment = self.portal.doc1.restrictedTraverse(
            f"++conversation++default/{new_id}",
        )

        # Add a reply to the CommentReplies adapter of the first comment
        re_comment = createObject("plone.Comment")
        re_comment.text = "Comment text"

        replies = IReplies(comment)

        new_re_id = replies.addComment(re_comment)

        # Remove the reply to the CommentReplies adapter
        del replies[new_re_id]

        # Make sure there is no comment left in CommentReplies
        self.assertEqual(len(replies), 0)

        # Make sure the first comment is still in the conversation
        self.assertEqual(conversation.total_comments(), 1)

    def test_traversal(self):
        # Create a nested structure of comment replies and check the traversal

        # make sure comments are traversable, have an id, absolute_url and
        # physical path
        conversation = IConversation(self.portal.doc1)

        comment1 = createObject("plone.Comment")
        comment1.text = "Comment text"

        conversation.addComment(comment1)

        comment = createObject("plone.Comment")
        comment.text = "Comment text"
        new_id = conversation.addComment(comment)
        comment = self.portal.doc1.restrictedTraverse(
            f"++conversation++default/{new_id}",
        )

        # Add a reply to the CommentReplies adapter of the first comment
        re_comment = createObject("plone.Comment")
        re_comment.text = "Comment text"
        replies = IReplies(comment)
        new_re_id = replies.addComment(re_comment)
        re_comment = self.portal.doc1.restrictedTraverse(
            f"++conversation++default/{new_re_id}",
        )

        # Add a reply to the reply
        re_re_comment = createObject("plone.Comment")
        re_re_comment.text = "Comment text"
        replies = IReplies(re_comment)
        new_re_re_id = replies.addComment(re_re_comment)
        re_re_comment = self.portal.doc1.restrictedTraverse(
            f"++conversation++default/{new_re_re_id}",
        )

        # Add a reply to the replies reply
        re_re_re_comment = createObject("plone.Comment")
        re_re_re_comment.text = "Comment text"
        replies = IReplies(re_re_comment)
        new_re_re_re_id = replies.addComment(re_re_re_comment)
        re_re_re_comment = self.portal.doc1.restrictedTraverse(
            f"++conversation++default/{new_re_re_re_id}",
        )

        self.assertEqual(
            ("", "plone", "doc1", "++conversation++default", str(new_id)),
            comment.getPhysicalPath(),
        )
        self.assertEqual(
            "http://nohost/plone/doc1/++conversation++default/" + str(new_id),
            comment.absolute_url(),
        )
        self.assertEqual(
            ("", "plone", "doc1", "++conversation++default", str(new_re_id)),
            re_comment.getPhysicalPath(),
        )
        self.assertEqual(
            "http://nohost/plone/doc1/++conversation++default/" + str(new_re_id),
            re_comment.absolute_url(),
        )
        self.assertEqual(
            (
                "",
                "plone",
                "doc1",
                "++conversation++default",
                str(new_re_re_id),
            ),
            re_re_comment.getPhysicalPath(),
        )
        self.assertEqual(
            "http://nohost/plone/doc1/++conversation++default/" + str(new_re_re_id),
            re_re_comment.absolute_url(),
        )
        self.assertEqual(
            (
                "",
                "plone",
                "doc1",
                "++conversation++default",
                str(new_re_re_re_id),
            ),
            re_re_re_comment.getPhysicalPath(),
        )
        self.assertEqual(
            "http://nohost/plone/doc1/++conversation++default/" + str(new_re_re_re_id),
            re_re_re_comment.absolute_url(),
        )
