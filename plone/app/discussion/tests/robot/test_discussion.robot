# ============================================================================
# Test basic discussion features (adding, replying, deleting)
# ============================================================================
#
# $ bin/robot-server plone.app.discussion.testing.PLONE_APP_DISCUSSION_ROBOT_TESTING
# $ bin/robot src/plone.app.discussion/src/plone/app/discussion/tests/robot/test_discussion.robot
#
# ============================================================================

*** Settings ***

Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Enable Discussion on a Document
  Given a logged-in Site Administrator
    and a document
   When I enable discussion on the document
   Then I can see a comment form on the document

Add Comment to a Document
  Given a logged-in Site Administrator
    and a document with discussion enabled
   When I add a comment
   Then I can see the comment below the document

#Reply to a comment on a Document
#  Given a logged-in Site Administrator
#    and a document with discussion enabled

#Delete Comment from a Document
#  Given a logged-in Site Administrator
#    and a document with discussion enabled


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


# Then

I can see a comment form on the document
  Go To  ${PLONE_URL}/my-document/view
  Wait until page contains  My Document
  Page should contain  Add comment
  Page should contain element  id=form-widgets-comment-text

I can see the comment below the document
  Go To  ${PLONE_URL}/my-document/view
  Page should contain  This is a comment
