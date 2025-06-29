"""Utility functions for plone.app.discussion."""


class CommentFlagProperty(object):
    """Property descriptor for flag count in IComment implementations.
    
    This descriptor dynamically computes the flag count from the flagged_by list,
    removing the need to maintain a redundant flag attribute.
    """
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        # If flagged_by doesn't exist or is None, return 0
        if not hasattr(instance, 'flagged_by') or instance.flagged_by is None:
            return 0
            
        # Return the length of the flagged_by list
        return len(instance.flagged_by)
    
    def __set__(self, instance, value):
        # This is a read-only property, so setting does nothing
        pass
