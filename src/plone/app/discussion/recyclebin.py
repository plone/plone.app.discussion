"""
RecycleBin support for comments and comment trees.

This module provides specialized handling for comment deletion and restoration
in the recycle bin system, ensuring comment threading relationships are preserved.
"""

from datetime import datetime
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IReplies
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface

import logging


logger = logging.getLogger("plone.app.discussion.recyclebin")


class ICommentRecycleBinSupport(Interface):
    """Interface for comment recycle bin operations"""

    def get_comment_tree_title(comment_tree):
        """Generate a meaningful title for a comment tree"""

    def create_comment_tree(comment, conversation):
        """Create a comment tree structure for recycle bin storage"""

    def should_create_comment_tree(comment, conversation):
        """Determine if a comment deletion should create a comment tree"""

    def restore_comment(comment_data, conversation, id_mapping=None):
        """Restore a single comment to a conversation"""

    def restore_comment_tree(comment_tree_data, conversation):
        """Restore a complete comment tree with all replies"""


@implementer(ICommentRecycleBinSupport)
class CommentRecycleBinSupport:
    """Utility providing recycle bin support for comments"""

    def get_comment_tree_title(self, comment_tree):
        """Generate a meaningful title for a comment tree"""
        comment_count = len(comment_tree.get("comments", []))
        root_comment = None

        # Try to find the root comment to get its text
        for comment, _ in comment_tree.get("comments", []):
            if getattr(comment, "comment_id", None) == comment_tree.get(
                "root_comment_id"
            ):
                root_comment = comment
                break

        # If we found the root comment, get a preview of its text
        comment_preview = ""
        if root_comment and hasattr(root_comment, "text"):
            # Take the first 30 characters of the text as a preview
            text = getattr(root_comment, "text", "")
            if text:
                if len(text) > 30:
                    comment_preview = text[:30] + "..."
                else:
                    comment_preview = text

        # Create a meaningful title
        if comment_preview:
            return f'Comment thread: "{comment_preview}" ({comment_count} comments)'
        else:
            return f"Comment thread ({comment_count} comments)"

    def create_comment_tree(self, comment, conversation):
        """Create a comment tree structure for deletion storage"""

        def get_comment_and_all_replies(comment, conversation):
            """Get a comment and all its replies recursively.

            Returns a list of tuples with (comment object, comment path)
            with the parent comment first, followed by all replies in depth-first order.
            """
            result = []
            comment_path = "/".join(comment.getPhysicalPath())
            result.append((comment, comment_path))

            # Get the replies to this comment
            replies = IReplies(comment)
            if replies:
                for reply_id in replies:
                    reply = replies[reply_id]
                    # Store the original parent ID to help with restoration
                    if not hasattr(reply, "original_parent_id"):
                        reply.original_parent_id = comment.id
                    # Recursively get this reply and its replies
                    result.extend(get_comment_and_all_replies(reply, conversation))

            return result

        # Get all comments in the tree
        comments_and_paths = get_comment_and_all_replies(comment, conversation)

        # Create the comment tree structure
        comment_tree = {
            "root_comment_id": getattr(comment, "comment_id", None),
            "comments": comments_and_paths,
            "deletion_date": datetime.now(),
        }

        return comment_tree

    def should_create_comment_tree(self, comment, conversation):
        """Determine if a comment deletion should create a comment tree.

        Returns True if the comment has replies, False otherwise.
        """
        replies = IReplies(comment)
        return len(replies) > 0 if replies else False

    def find_parent_comment(
        self, comment, original_in_reply_to, conversation, id_mapping=None
    ):
        """Helper method to find parent comment during restoration"""
        id_mapping = id_mapping or {}
        if original_in_reply_to is None or original_in_reply_to == 0:
            return False, None

        # First check if parent exists directly (not previously deleted)
        if original_in_reply_to in conversation:
            return True, original_in_reply_to

        # Then check if it was restored with a different ID using mapping
        if str(original_in_reply_to) in id_mapping:
            # Use the ID mapping to find the new ID
            new_parent_id = id_mapping[str(original_in_reply_to)]
            return True, new_parent_id

        # Look through all comments for original_id matching our in_reply_to
        for comment_id in conversation.keys():
            comment_obj = conversation[comment_id]
            comment_original_id = getattr(comment_obj, "original_id", None)
            if comment_original_id is not None and str(comment_original_id) == str(
                original_in_reply_to
            ):
                # Found the parent with a new ID
                return True, comment_id

        # No parent found
        return False, None

    def restore_comment(self, item_data, target_conversation=None):
        """Enhanced restoration method for comments that preserves reply relationships"""
        obj = item_data["object"]
        site = getSite()

        # Try to find the original conversation if not provided
        if target_conversation is None:
            parent_path = item_data["parent_path"]
            try:
                conversation = site.unrestrictedTraverse(parent_path)
            except (KeyError, AttributeError):
                logger.warning(
                    f"Cannot restore comment: conversation no longer exists at {parent_path}"
                )
                return None
        else:
            conversation = target_conversation

        if not IConversation.providedBy(conversation):
            logger.warning("Cannot restore comment: parent is not a conversation")
            return None

        # Store the original comment ID before restoration
        original_id = getattr(obj, "comment_id", None)
        original_in_reply_to = getattr(obj, "in_reply_to", None)

        # Track comment relationships using a request-based dictionary
        request = getRequest()
        if request and not hasattr(request, "_comment_restore_mapping"):
            request._comment_restore_mapping = {}

        # Initialize mapping if needed
        mapping = getattr(request, "_comment_restore_mapping", {})
        conversation_path = "/".join(conversation.getPhysicalPath())
        if conversation_path not in mapping:
            mapping[conversation_path] = {}

        id_mapping = mapping[conversation_path]

        # Check if the parent comment exists in the conversation
        parent_found, new_parent_id = self.find_parent_comment(
            obj, original_in_reply_to, conversation, id_mapping
        )

        # Update the in_reply_to reference or make it a top-level comment
        if parent_found:
            obj.in_reply_to = new_parent_id
        else:
            # If no parent was found, make this a top-level comment
            obj.in_reply_to = None

        # Store the original ID for future reference
        if not hasattr(obj, "original_id"):
            obj.original_id = original_id

        # Add the comment to the conversation
        new_id = conversation.addComment(obj)

        # Store the mapping of original ID to new ID
        if original_id is not None:
            id_mapping[str(original_id)] = new_id

        # Return the restored comment
        return conversation[new_id]

    def restore_comment_tree(self, item_data, target_conversation=None):
        """Restore a comment tree with all its replies while preserving relationships"""
        comment_tree = item_data["object"]
        root_comment_id = comment_tree.get("root_comment_id")
        comments_to_restore = comment_tree.get("comments", [])

        logger.info(
            f"Attempting to restore comment tree with root_comment_id: {root_comment_id}"
        )
        logger.info(f"Found {len(comments_to_restore)} comments to restore")

        if not comments_to_restore:
            logger.warning("Cannot restore comment tree: no comments found in tree")
            return None

        site = getSite()

        # Try to find the original conversation if not provided
        if target_conversation is None:
            parent_path = item_data["parent_path"]
            try:
                conversation = site.unrestrictedTraverse(parent_path)
            except (KeyError, AttributeError):
                logger.warning(
                    f"Cannot restore comment tree: conversation no longer exists at {parent_path}"
                )
                return None
        else:
            conversation = target_conversation

        if not IConversation.providedBy(conversation):
            logger.warning("Cannot restore comment tree: parent is not a conversation")
            return None

        # First extract all comments and create a mapping of original IDs
        # to comment objects for quick lookup
        comment_dict = {}
        id_mapping = {}  # Will map original IDs to new IDs

        # Process comments to build reference dictionary
        for comment_obj, _ in comments_to_restore:
            # Store original values we'll need for restoration
            original_id = getattr(comment_obj, "comment_id", None)
            original_in_reply_to = getattr(comment_obj, "in_reply_to", None)

            logger.info(
                f"Processing comment with ID: {original_id}, in_reply_to: {original_in_reply_to}"
            )

            comment_obj.original_id = (
                original_id  # Store original ID for future reference
            )

            # Store in dictionary for quick access
            comment_dict[original_id] = {
                "comment": comment_obj,
                "in_reply_to": original_in_reply_to,
            }

        # Find the root comment
        root_comment = None
        if root_comment_id in comment_dict:
            root_comment = comment_dict[root_comment_id]["comment"]
        else:
            # Try to find a top-level comment to use as root
            for comment_id, comment_data in comment_dict.items():
                in_reply_to = comment_data["in_reply_to"]
                if in_reply_to == 0 or in_reply_to is None:
                    # Found a top-level comment, use as root
                    root_comment = comment_data["comment"]
                    root_comment_id = comment_id
                    break

            # If still no root, use the first comment
            if not root_comment and comment_dict:
                first_key = list(comment_dict.keys())[0]
                root_comment = comment_dict[first_key]["comment"]
                root_comment_id = first_key

        if not root_comment:
            logger.error(
                "Cannot restore comment tree: no valid root comment could be determined"
            )
            return None

        # Check if the parent comment exists
        original_in_reply_to = getattr(root_comment, "in_reply_to", None)
        parent_found, new_parent_id = self.find_parent_comment(
            root_comment, original_in_reply_to, conversation
        )

        if parent_found:
            root_comment.in_reply_to = new_parent_id
        else:
            root_comment.in_reply_to = None

        # Add the root comment to the conversation
        new_root_id = conversation.addComment(root_comment)
        id_mapping[root_comment_id] = new_root_id

        # Now restore all child comments, skipping the root comment
        remaining_comments = {
            k: v for k, v in comment_dict.items() if k != root_comment_id
        }

        # Track successfully restored comments
        restored_count = 1  # Start with 1 for root

        # Keep trying to restore comments until no more can be restored
        max_passes = 10  # Limit passes to avoid infinite loops
        current_pass = 0

        while remaining_comments and current_pass < max_passes:
            current_pass += 1
            restored_in_pass = 0

            # Copy keys to avoid modifying dict during iteration
            comment_ids = list(remaining_comments.keys())

            for comment_id in comment_ids:
                comment_data = remaining_comments[comment_id]
                comment_obj = comment_data["comment"]
                original_in_reply_to = comment_data["in_reply_to"]

                # Try to find the parent in our mapping
                parent_found = False
                new_parent_id = None

                # If original parent was the root comment
                if str(original_in_reply_to) == str(root_comment_id):
                    parent_found = True
                    new_parent_id = new_root_id
                # Or if it was another already restored comment
                elif str(original_in_reply_to) in id_mapping:
                    parent_found = True
                    new_parent_id = id_mapping[str(original_in_reply_to)]
                # Or try to find it directly in the conversation
                else:
                    parent_found, new_parent_id = self.find_parent_comment(
                        comment_obj, original_in_reply_to, conversation, id_mapping
                    )

                if parent_found:
                    # We found the parent, update reference and restore
                    comment_obj.in_reply_to = new_parent_id

                    # Store original ID for future reference
                    if not hasattr(comment_obj, "original_id"):
                        comment_obj.original_id = comment_id

                    # Add to conversation
                    try:
                        new_id = conversation.addComment(comment_obj)
                        id_mapping[comment_id] = new_id
                        del remaining_comments[comment_id]
                        restored_in_pass += 1
                    except Exception as e:
                        logger.error(f"Error restoring comment {comment_id}: {e}")

            # If we didn't restore any comments in this pass and still have comments left,
            # something is wrong with the parent references
            if restored_in_pass == 0 and remaining_comments:
                # Make any remaining comments top-level comments
                restored_in_pass += self.handle_orphaned_comments(
                    remaining_comments, conversation, id_mapping
                )

                # Break out of the loop since we've tried our best
                break

            restored_count += restored_in_pass

            # If all comments were restored, exit the loop
            if not remaining_comments:
                break

        logger.info(f"Restored {restored_count} comments from comment tree")

        # Return the root comment as the result
        return conversation.get(new_root_id) if new_root_id in conversation else None

    def handle_orphaned_comments(self, remaining_comments, conversation, id_mapping):
        """Handle comments whose parents cannot be found

        Makes orphaned comments top-level comments rather than losing them.

        Args:
            remaining_comments: Dictionary of remaining comments to process
            conversation: The conversation container
            id_mapping: Mapping of original IDs to new IDs
        """
        orphaned_count = 0
        for comment_id, comment_data in list(remaining_comments.items()):
            try:
                comment_obj = comment_data["comment"]
                # Make it a top-level comment
                comment_obj.in_reply_to = None

                # Ensure original_id is preserved
                if not hasattr(comment_obj, "original_id"):
                    comment_obj.original_id = comment_id

                # Add to conversation
                new_id = conversation.addComment(comment_obj)
                id_mapping[comment_id] = new_id
                del remaining_comments[comment_id]
                orphaned_count += 1
                logger.info(
                    f"Restored orphaned comment {comment_id} as top-level comment"
                )
            except Exception as e:
                logger.error(f"Error restoring orphaned comment {comment_id}: {str(e)}")

        return orphaned_count
