*** Keywords ***

I enable discussion on the document
  Go To  ${PLONE_URL}/my-document/edit
  Get Text  body  contains  Settings
  Click  .autotoc-nav >> "Settings"
  Select Options By  id=formfield-form-widgets-IAllowDiscussion-allow_discussion >> select  text  Yes
  Click  "Save"

I add a comment
  Type Text  id=form-widgets-comment-text  This is a comment
  Click  css=button[name="form.buttons.comment"]

I can see that the comment is gone
  Go To  ${PLONE_URL}/my-document/view
  Get Element Count  css=.comment-body  ==  0
