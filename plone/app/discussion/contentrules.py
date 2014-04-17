""" Content rules handlers
"""
from Acquisition import aq_parent
from plone.app.contentrules.handlers import execute
from plone.stringinterp import adapters

def execute_comment(event):
    """ Execute comment content rules
    """
    execute(event.object, event)
