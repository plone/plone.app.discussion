"""Content filtering utilities for comment moderation."""

import re
from plone.app.discussion.interfaces import _
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IDiscussionSettings
from zope.component import queryUtility
from zope.i18n import translate

import logging

logger = logging.getLogger("plone.app.discussion.filter")


class CommentContentFilter:
    """Utility for filtering comment content based on configured rules."""

    def __init__(self, context=None, request=None):
        self.context = context
        self.request = request
        self._settings = None

    @property
    def settings(self):
        """Get discussion settings from registry."""
        if self._settings is None:
            registry = queryUtility(IRegistry)
            if registry is not None:
                self._settings = registry.forInterface(IDiscussionSettings, check=False)
        return self._settings

    def is_enabled(self):
        """Check if content filtering is enabled."""
        enabled = getattr(self.settings, 'content_filter_enabled', False)
        return enabled

    def get_filtered_words(self):
        """Get list of filtered words from settings."""
        if not self.settings:
            return []
        
        words_text = getattr(self.settings, 'filtered_words', '') or ''
        if not words_text.strip():
            return []
        
        # Split by lines and filter out empty lines
        return [word.strip() for word in words_text.split('\n') if word.strip()]

    def compile_pattern(self, word):
        """Compile a single word/phrase into a regex pattern."""
        # Escape special regex characters except for our wildcard *
        escaped_word = re.escape(word)
        # Replace escaped asterisks with regex wildcard pattern
        pattern = escaped_word.replace(r'\*', r'[^\s]*')
        
        case_sensitive = getattr(self.settings, 'filter_case_sensitive', False)
        whole_words_only = getattr(self.settings, 'filter_whole_words_only', True)
        
        if whole_words_only:
            pattern = r'\b' + pattern + r'\b'
        
        flags = 0 if case_sensitive else re.IGNORECASE
        
        try:
            return re.compile(pattern, flags)
        except re.error:
            return None

    def check_content(self, text):
        """
        Check if text contains any filtered content.
        
        Returns:
            dict: {
                'filtered': bool,
                'matches': list of matched words/phrases,
                'action': str - action to take if filtered
            }
        """
        # Determine the filter action based on moderation settings
        filter_action = getattr(self.settings, 'filter_action', 'moderate')
        moderation_enabled = getattr(self.settings, 'moderation_enabled', False)
        
        # If moderation is disabled, force action to 'reject'
        if not moderation_enabled:
            filter_action = 'reject'
        
        result = {
            'filtered': False,
            'matches': [],
            'action': filter_action
        }
        
        if not self.is_enabled() or not text:
            return result
        
        filtered_words = self.get_filtered_words()
        if not filtered_words:
            return result
        
        for word in filtered_words:
            pattern = self.compile_pattern(word)
            if pattern and pattern.search(text):
                logger.debug(f"Content filter match: '{word}' found in text")
                result['filtered'] = True
                result['matches'].append(word)
        
        return result

    def get_rejection_message(self, matches=None):
        """Get user-friendly message for rejected comments."""
        if matches:
            msgid = _(
                "comment_filtered_with_words",
                default="Your comment contains filtered content and cannot be posted. "
                "Please remove or modify the following: ${words}",
                mapping={'words': ', '.join(matches)}
            )
        else:
            msgid = _(
                "comment_filtered",
                default="Your comment contains filtered content and cannot be posted. "
                "Please review and modify your comment."
            )
        
        return translate(msgid, context=self.request) if self.request else msgid.default

    def get_moderation_message(self):
        """Get user-friendly message for moderated comments."""
        msgid = _(
            "comment_filtered_moderation",
            default="Your comment has been submitted for review due to content "
            "that requires moderation approval."
        )
        
        return translate(msgid, context=self.request) if self.request else msgid.default


def get_content_filter(context=None, request=None):
    """Factory function to get a content filter instance."""
    return CommentContentFilter(context=context, request=request)
