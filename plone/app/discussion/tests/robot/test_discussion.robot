*** Settings ***

Resource  plone/app/robotframework/browser.robot
Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown

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

Reply to a comment on a Document
  Given a logged-in Site Administrator
    and a document with discussion enabled
    and I add a comment
   When I reply to a comment
   Then I can see the reply

Delete Comment from a Document
  Given a logged-in Site Administrator
    and a document with discussion enabled
    and I add a comment
   When I delete the comment
   Then I can see that the comment is gone

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

I reply to a comment
  Click  "Reply"
  Fill Text  css=div[id^=formfield-form-widgets-new] > textarea  My reply text
  Click  css=.discussion button[name="form.buttons.comment"]

I delete the comment
  Click  css=button[name="form.button.DeleteComment"]

# Then

I can see a comment form on the document
  Go To  ${PLONE_URL}/my-document/view
  Get Text  h1  ==  My Document
  Get Text  legend  ==  Add comment
  Get Element  id=form-widgets-comment-text

I can see the comment below the document
  Go To  ${PLONE_URL}/my-document/view
  Get Text  css=.comment-body > p  ==  This is a comment

I can see the reply
  Go To  ${PLONE_URL}/my-document/view
  Get Text  css=.level-1 .comment-body > p  ==  My reply text
