""" Content rules handlers
"""
from plone.app.contentrules.handlers import execute

def execute_comment(event):
    """ Execute comment content rules
    """
    execute(event.object, event)
