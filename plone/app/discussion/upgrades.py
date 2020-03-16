# -*- coding: utf-8 -*-
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

import logging


default_profile = 'profile-plone.app.discussion:default'
logger = logging.getLogger('plone.app.discussion')


def update_registry(context):
    registry = getUtility(IRegistry)
    registry.registerInterface(IDiscussionSettings)


def update_rolemap(context):
    context.runImportStepFromProfile(default_profile, 'rolemap')


def upgrade_comment_workflows_retain_current_workflow(context):
    # If the current comment workflow is the one_state_workflow, running our
    # import step will change it to comment_one_state_workflow.  This is good.
    # If it was anything else, we should restore this.  So get the original
    # chain.
    portal_type = 'Discussion Item'
    wf_tool = getToolByName(context, 'portal_workflow')
    orig_chain = list(wf_tool.getChainFor(portal_type))

    # Run the workflow step.  This sets the chain to
    # comment_one_state_workflow.
    context.runImportStepFromProfile(default_profile, 'workflow')

    # Restore original workflow chain if needed.
    old_workflow = 'one_state_workflow'
    if old_workflow not in orig_chain:
        # Restore the chain.  Probably comment_review_workflow.
        wf_tool.setChainForPortalTypes([portal_type], orig_chain)
    elif len(orig_chain) > 1:
        # This is strange, but I guess it could happen.
        if old_workflow in orig_chain:
            # Replace with new one.
            idx = orig_chain.index(old_workflow)
            orig_chain[idx] = 'comment_one_state_workflow'
        # Restore the chain.
        wf_tool.setChainForPortalTypes([portal_type], orig_chain)


def upgrade_comment_workflows_apply_rolemapping(context):
    # Now go over the comments, update their role mappings, and reindex the
    # allowedRolesAndUsers index.
    portal_type = 'Discussion Item'
    catalog = getToolByName(context, 'portal_catalog')
    wf_tool = getToolByName(context, 'portal_workflow')
    new_chain = list(wf_tool.getChainFor(portal_type))
    workflows = [wf_tool.getWorkflowById(wf_id) for wf_id in new_chain]
    for brain in catalog.unrestrictedSearchResults(portal_type=portal_type):
        try:
            comment = brain.getObject()
            for wf in workflows:
                wf.updateRoleMappingsFor(comment)
            comment.reindexObjectSecurity()
        except (AttributeError, KeyError):
            logger.info('Could not reindex comment {0}'.format(brain.getURL()))


def upgrade_comment_workflows(context):
    upgrade_comment_workflows_retain_current_workflow(context)
    upgrade_comment_workflows_apply_rolemapping(context)


def add_js_to_plone_legacy(context):
    context.runImportStepFromProfile(default_profile, 'plone.app.registry')


def extend_review_workflow(context):
    """Apply changes made to review workflow."""
    upgrade_comment_workflows_retain_current_workflow(context)
