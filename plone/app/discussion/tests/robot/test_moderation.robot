*** Settings ***

Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown


*** Test Cases ***

Add a Comment to a Document and bulk delete it
  Given a logged-in Site Administrator
    and workflow multiple enabled
    and a document with discussion enabled
  When I add a comment and delete it
  Then I can not see the comment below the document

Last history entry is shown
  Given a logged-in Site Administrator
    and workflow multiple enabled
    and a document with discussion enabled
  When I add a comment
  Then I can see the last history entry in moderation view


*** Keywords ***

# Given

a logged-in Site Administrator
  Enable autologin as  Site Administrator

a document
  Create content  type=Document  id=my-document  title=My Document

a document with discussion enabled
  a document
  I enable discussion on the document


# When

I enable discussion on the document
  Go To  ${PLONE_URL}/my-document/edit
  Wait until page contains  Settings
  Click Link  Settings
  Wait until element is visible  name=form.widgets.IAllowDiscussion.allow_discussion:list
  Select From List  name=form.widgets.IAllowDiscussion.allow_discussion:list  True
  Click Button  Save

I add a comment
  Wait until page contains element  id=form-widgets-comment-text
  Input Text  id=form-widgets-comment-text  This is a comment
  Click Button  Comment

I add a comment and delete it
  Wait until page contains element  id=form-widgets-comment-text
  Input Text  id=form-widgets-comment-text  This is a comment
  Click Button  Comment
  Go To  ${PLONE_URL}/@@moderate-comments?review_state=all
  Wait until page contains element  name=form.select.BulkAction
  Select from list by value   xpath://select[@name='form.select.BulkAction']  delete
  Select Checkbox  name=check_all
  Click Button  Apply
  Wait Until Page Does Not Contain  This is a comment

workflow multiple enabled
  Go To  ${PLONE_URL}/@@content-controlpanel?type_id=Discussion%20Item&new_workflow=comment_review_workflow
  Click Button  Save

# Then

I can not see the comment below the document
  Go To  ${PLONE_URL}/my-document/view
  Wait until page contains  My Document
  Page should not contain  This is a comment

I can see the last history entry in moderation view
  Go To  ${PLONE_URL}/@@moderate-comments?review_state=all
  Wait until page contains element  name=form.select.BulkAction
  Page should contain  Create
