*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: Allow comments for Link Type
  Given a logged-in manager
    and Globally enabled comments
    and the types control panel
   When I select 'Link' in types dropdown
    and Allow discussion
   Then Wait until page contains  Content Settings
   When I add new Link 'my_link'
    Then Link 'my_link' should have comments enabled


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in manager
  Enable autologin as  Manager

the types control panel
  Go to  ${PLONE_URL}/@@content-controlpanel
  Wait until page contains  Content Settings

Globally enabled comments
  Go to  ${PLONE_URL}/@@discussion-settings
  Wait until page contains  Discussion settings
  Select checkbox  name=form.widgets.globally_enabled:list
  Click button  Save



# --- WHEN -------------------------------------------------------------------

I select '${content_type}' in types dropdown
  Select from list by label  name=type_id  ${content_type}
  Wait until page contains  Globally addable

Allow discussion
  Select checkbox  name=allow_discussion:boolean
  Click Button  Save

I add new Link '${id}'
  Go to  ${PLONE_URL}
  Wait until page contains  Plone site
  Create content  type=Link  id=${id}  title=${id}  remoteUrl=http://www.starzel.de


# --- THEN -------------------------------------------------------------------

Link '${id}' should have comments enabled
  Go to  ${PLONE_URL}/${id}
  Wait until page contains  ${id}
  Page should contain element  xpath=//div[@id="commenting"]
