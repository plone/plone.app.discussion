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
Resource  plone/app/robotframework/keywords.robot

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

# This test will fail as member has to input email due to bug in p.a.discussion
Add Comment as anon to a Document
  Given Log in  admin  secret
    and I enable anon and email anon global and discussion on the document

  Given a anon user
   When I add a comment as anon
   Then I can see the anon comment below the document

  Given a logged-in Member
   When I add a comment as member
   Then I can see the member comment below the document

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

a anon user
  Log out
  Go To  ${PLONE_URL}/my-document/

a logged-in Member
  Log in as test user
  Go To  ${PLONE_URL}/my-document/

a document
  Create content  type=Document  id=my-document  title=My Document

a document with discussion enabled
  a document
  I enable discussion on the document

a document with anon discussion enabled
  a document
  I enable discussion on the document

# When

I enable anon and email anon global and discussion on the document
  Go To  ${PLONE_URL}/@@discussion-settings
  Select Checkbox  name=form.widgets.anonymous_comments:list
  Select Checkbox  name=form.widgets.anonymous_email_enabled:list
  Click Button  Save
  Go To  ${PLONE_URL}/++add++Document
  Input Text  form-widgets-IDublinCore-title  My Document
  Click Button  Save
  Go To  ${PLONE_URL}/my-document/content_status_history
  select radio button  workflow_action  publish
  Click Button  Save
  I enable discussion on the document

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

I add a comment as anon
  Wait until page contains element  id=form-widgets-comment-text
  Input Text  id=form-widgets-comment-text  This is a comment
  Input Text  id=form-widgets-author_email  test@plone.org
  Input Text  id=form-widgets-author_name  AnonName
  Click Button  Comment

I add a comment as member
  Wait until page contains element  id=form-widgets-comment-text
  Input Text  id=form-widgets-comment-text  This is a member comment
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

I can see the anon comment below the document
  Go To  ${PLONE_URL}/my-document/view
  Page should contain  This is a comment
  Page should contain  AnonName

I can see the member comment below the document
  Go To  ${PLONE_URL}/my-document/view
  Page should contain  This is a member comment
