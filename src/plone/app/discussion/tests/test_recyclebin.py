"""
Tests for comment recycle bin support functionality.
"""

from datetime import datetime
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.recyclebin import CommentRecycleBinSupport
from plone.app.discussion.recyclebin import ICommentRecycleBinSupport
from plone.app.discussion.testing import PLONE_APP_DISCUSSION_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import createObject
from zope.component import getUtility

import unittest


class TestCommentRecycleBinSupport(unittest.TestCase):
    """Test cases for comment recycle bin support functionality."""

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # Create a document for testing
        self.portal.invokeFactory("Document", "doc1", title="Document 1")
        self.doc1 = self.portal["doc1"]

        # Enable comments on the document
        from plone.app.discussion.interfaces import IDiscussionSettings
        from plone.registry.interfaces import IRegistry

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True
        settings.edit_comment_enabled = True
        settings.delete_own_comment_enabled = True

        # Get the conversation
        self.conversation = IConversation(self.doc1)

        # Create test utility instance
        self.utility = CommentRecycleBinSupport()

    def test_utility_interface(self):
        """Test that the utility provides the correct interface."""
        self.assertTrue(ICommentRecycleBinSupport.providedBy(self.utility))

    def test_get_comment_tree_title_with_preview(self):
        """Test generating title for comment tree with text preview."""
        # Create a mock comment tree structure
        comment = createObject("plone.Comment")
        comment.comment_id = 123
        comment.text = "This is a test comment with some long text content"

        comment_tree = {
            "root_comment_id": 123,
            "comments": [(comment, "/path/to/comment")],
        }

        title = self.utility.get_comment_tree_title(comment_tree)
        expected = 'Comment thread: "This is a test comment with s..." (1 comments)'
        self.assertEqual(title, expected)

    def test_get_comment_tree_title_short_text(self):
        """Test generating title for comment tree with short text."""
        comment = createObject("plone.Comment")
        comment.comment_id = 123
        comment.text = "Short text"

        comment_tree = {
            "root_comment_id": 123,
            "comments": [(comment, "/path/to/comment")],
        }

        title = self.utility.get_comment_tree_title(comment_tree)
        expected = 'Comment thread: "Short text" (1 comments)'
        self.assertEqual(title, expected)

    def test_get_comment_tree_title_no_text(self):
        """Test generating title for comment tree without text."""
        comment = createObject("plone.Comment")
        comment.comment_id = 123
        # No text attribute

        comment_tree = {
            "root_comment_id": 123,
            "comments": [(comment, "/path/to/comment")],
        }

        title = self.utility.get_comment_tree_title(comment_tree)
        expected = "Comment thread (1 comments)"
        self.assertEqual(title, expected)

    def test_get_comment_tree_title_no_root_comment(self):
        """Test generating title when root comment is not found."""
        comment = createObject("plone.Comment")
        comment.comment_id = 456  # Different from root_comment_id

        comment_tree = {
            "root_comment_id": 123,
            "comments": [(comment, "/path/to/comment")],
        }

        title = self.utility.get_comment_tree_title(comment_tree)
        expected = "Comment thread (1 comments)"
        self.assertEqual(title, expected)

    def test_create_comment_tree_single_comment(self):
        """Test creating a comment tree with a single comment."""
        # Add a comment to the conversation
        comment = createObject("plone.Comment")
        comment.text = "Test comment"
        comment_id = self.conversation.addComment(comment)
        comment_obj = self.conversation[comment_id]

        # Create comment tree
        comment_tree = self.utility.create_comment_tree(comment_obj, self.conversation)

        self.assertEqual(comment_tree["root_comment_id"], comment_id)
        self.assertEqual(len(comment_tree["comments"]), 1)
        self.assertIsInstance(comment_tree["deletion_date"], datetime)

    def test_should_create_comment_tree_no_replies(self):
        """Test should_create_comment_tree with comment that has no replies."""
        # Add a comment to the conversation
        comment = createObject("plone.Comment")
        comment.text = "Test comment"
        comment_id = self.conversation.addComment(comment)
        comment_obj = self.conversation[comment_id]

        # Should not create tree for single comment
        should_create = self.utility.should_create_comment_tree(
            comment_obj, self.conversation
        )
        self.assertFalse(should_create)

    def test_should_create_comment_tree_with_replies(self):
        """Test should_create_comment_tree with comment that has replies."""
        # Add parent comment
        parent_comment = createObject("plone.Comment")
        parent_comment.text = "Parent comment"
        parent_id = self.conversation.addComment(parent_comment)
        parent_obj = self.conversation[parent_id]

        # Add reply comment
        reply_comment = createObject("plone.Comment")
        reply_comment.text = "Reply comment"
        reply_comment.in_reply_to = parent_id
        self.conversation.addComment(reply_comment)

        # Should create tree for comment with replies
        should_create = self.utility.should_create_comment_tree(
            parent_obj, self.conversation
        )
        self.assertTrue(should_create)

    def test_find_parent_comment_direct_parent(self):
        """Test finding parent comment that exists directly in conversation."""
        # Add parent comment
        parent_comment = createObject("plone.Comment")
        parent_comment.text = "Parent comment"
        parent_id = self.conversation.addComment(parent_comment)

        # Add child comment
        child_comment = createObject("plone.Comment")
        child_comment.text = "Child comment"
        child_comment.in_reply_to = parent_id
        self.conversation.addComment(child_comment)

        # Test finding parent
        found, found_id = self.utility.find_parent_comment(
            child_comment, parent_id, self.conversation
        )

        self.assertTrue(found)
        self.assertEqual(found_id, parent_id)

    def test_find_parent_comment_no_parent(self):
        """Test finding parent comment when none exists."""
        comment = createObject("plone.Comment")
        comment.text = "Top-level comment"

        found, found_id = self.utility.find_parent_comment(
            comment, None, self.conversation
        )

        self.assertFalse(found)
        self.assertIsNone(found_id)

    def test_find_parent_comment_with_mapping(self):
        """Test finding parent comment using ID mapping."""
        # Add a comment
        comment = createObject("plone.Comment")
        comment.text = "Test comment"
        comment_id = self.conversation.addComment(comment)

        # Create ID mapping
        id_mapping = {"123": comment_id}

        # Test finding parent using mapping
        found, found_id = self.utility.find_parent_comment(
            comment, 123, self.conversation, id_mapping
        )

        self.assertTrue(found)
        self.assertEqual(found_id, comment_id)

    def test_restore_comment_top_level(self):
        """Test restoring a top-level comment."""
        # Create a comment to restore
        comment = createObject("plone.Comment")
        comment.text = "Test comment to restore"
        comment.comment_id = 123
        comment.in_reply_to = None

        # Create item data for restoration
        item_data = {
            "object": comment,
            "parent_path": "/".join(self.conversation.getPhysicalPath()),
        }

        # Restore the comment
        restored_comment = self.utility.restore_comment(item_data, self.conversation)

        self.assertIsNotNone(restored_comment)
        self.assertEqual(restored_comment.text, "Test comment to restore")
        self.assertEqual(len(self.conversation), 1)

    def test_restore_comment_with_parent(self):
        """Test restoring a comment that replies to an existing comment."""
        # Add parent comment first
        parent_comment = createObject("plone.Comment")
        parent_comment.text = "Parent comment"
        parent_id = self.conversation.addComment(parent_comment)

        # Create a reply comment to restore
        reply_comment = createObject("plone.Comment")
        reply_comment.text = "Reply comment to restore"
        reply_comment.comment_id = 124
        reply_comment.in_reply_to = parent_id

        # Create item data for restoration
        item_data = {
            "object": reply_comment,
            "parent_path": "/".join(self.conversation.getPhysicalPath()),
        }

        # Restore the reply comment
        restored_comment = self.utility.restore_comment(item_data, self.conversation)

        self.assertIsNotNone(restored_comment)
        self.assertEqual(restored_comment.text, "Reply comment to restore")
        self.assertEqual(restored_comment.in_reply_to, parent_id)
        self.assertEqual(len(self.conversation), 2)

    def test_restore_comment_orphaned(self):
        """Test restoring a comment whose parent no longer exists."""
        # Create a reply comment to restore (parent doesn't exist)
        reply_comment = createObject("plone.Comment")
        reply_comment.text = "Orphaned reply comment"
        reply_comment.comment_id = 125
        reply_comment.in_reply_to = 999  # Non-existent parent

        # Create item data for restoration
        item_data = {
            "object": reply_comment,
            "parent_path": "/".join(self.conversation.getPhysicalPath()),
        }

        # Restore the orphaned comment
        restored_comment = self.utility.restore_comment(item_data, self.conversation)

        self.assertIsNotNone(restored_comment)
        self.assertEqual(restored_comment.text, "Orphaned reply comment")
        self.assertIsNone(restored_comment.in_reply_to)  # Should become top-level
        self.assertEqual(len(self.conversation), 1)

    def test_restore_comment_tree_simple(self):
        """Test restoring a simple comment tree."""
        # Create a simple comment tree structure
        root_comment = createObject("plone.Comment")
        root_comment.text = "Root comment"
        root_comment.comment_id = 100
        root_comment.in_reply_to = None

        reply_comment = createObject("plone.Comment")
        reply_comment.text = "Reply comment"
        reply_comment.comment_id = 101
        reply_comment.in_reply_to = 100

        comment_tree = {
            "root_comment_id": 100,
            "comments": [
                (root_comment, "/path/to/root"),
                (reply_comment, "/path/to/reply"),
            ],
        }

        item_data = {
            "object": comment_tree,
            "parent_path": "/".join(self.conversation.getPhysicalPath()),
        }

        # Restore the comment tree
        restored_root = self.utility.restore_comment_tree(item_data, self.conversation)

        self.assertIsNotNone(restored_root)
        self.assertEqual(restored_root.text, "Root comment")
        self.assertEqual(len(self.conversation), 2)

        # Check that the reply relationship is preserved
        comments = list(self.conversation.values())
        reply = None
        for comment in comments:
            if comment.text == "Reply comment":
                reply = comment
                break

        self.assertIsNotNone(reply)
        self.assertEqual(reply.in_reply_to, restored_root.comment_id)

    def test_handle_orphaned_comments(self):
        """Test handling of orphaned comments."""
        orphaned_comment = createObject("plone.Comment")
        orphaned_comment.text = "Orphaned comment"
        orphaned_comment.comment_id = 200

        remaining_comments = {
            200: {
                "comment": orphaned_comment,
                "in_reply_to": 999,  # Non-existent parent
            }
        }

        id_mapping = {}

        # Handle orphaned comments
        orphaned_count = self.utility.handle_orphaned_comments(
            remaining_comments, self.conversation, id_mapping
        )

        self.assertEqual(orphaned_count, 1)
        self.assertEqual(len(remaining_comments), 0)  # Should be cleared
        self.assertEqual(len(self.conversation), 1)

        # Check that the comment became top-level
        restored_comment = list(self.conversation.values())[0]
        self.assertEqual(restored_comment.text, "Orphaned comment")
        self.assertIsNone(restored_comment.in_reply_to)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
