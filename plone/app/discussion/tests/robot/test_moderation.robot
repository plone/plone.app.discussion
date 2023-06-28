*** Settings ***

Resource  plone/app/robotframework/browser.robot
Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown


*** Test Cases ***

Add a Comment to a Document and bulk delete it
  Given a logged-in Site Administrator
    and workflow multiple enabled
    and a document with discussion enabled
  When I add a comment and delete it
  Then I can see that the comment is gone

Last history entry is shown
  Given a logged-in Site Administrator
    and workflow multiple enabled
    and a document with discussion enabled
  When I add a comment
  Then I can see the last history entry in moderation view


*** Keywords ***

Select And Check
  [Arguments]  ${selector}  ${value}
  Select From List by Value  ${selector}  ${value}
  ${selected_value} =  Get Selected List Value  ${selector}
  Should Be Equal As Strings  ${selected_value}  ${value}

# Given

a logged-in Site Administrator
  Enable autologin as  Site Administrator

a document
  Create content  type=Document  id=my-document  title=My Document

a document with discussion enabled
  a document
  I enable discussion on the document


# When

I add a comment and delete it
  Fill Text  id=form-widgets-comment-text  This is a comment
  Click  css=button[name="form.buttons.comment"]
  Go To  ${PLONE_URL}/@@moderate-comments?review_state=all
  Get Text  body  contains  Bulk Actions
  Select Options By  select[name="form.select.BulkAction"]  text  Delete
  Check Checkbox  input[name="check_all"]
  Click  "Apply"
  Get Element Count  table > tbody > tr  ==  0.0

workflow multiple enabled
  Go To  ${PLONE_URL}/@@content-controlpanel?type_id=Discussion%20Item&new_workflow=comment_review_workflow
  Click  "Save"

# Then

I can not see the comment below the document
  Go To  ${PLONE_URL}/my-document/view
  Get Text  body  contains My Document
  Page should not contain  This is a comment

I can see the last history entry in moderation view
  Go To  ${PLONE_URL}/@@moderate-comments?review_state=all
  Get Text  body  contains  Bulk Actions
  Get Text  table  contains  Create
