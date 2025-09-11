*** Settings ***

Resource  plone/app/robotframework/browser.robot
Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown

*** Test Cases ***

Scenario: Allow comments for Link Type
  Given a logged-in manager
    and Globally enabled comments
    and the types control panel
   When I select 'Link' in types dropdown
    and Allow discussion
   Then Wait For Condition    Text    //body   contains    Content Settings

   When I add new Link 'my_link'
   Then Link 'my_link' should have comments enabled


*** Keywords ***

# GIVEN

a logged-in manager
    Enable autologin as    Manager

the types control panel
    Go to    ${PLONE_URL}/@@content-controlpanel
    Wait For Condition    Text    //body   contains    Content Settings

Globally enabled comments
    Go to    ${PLONE_URL}/@@discussion-settings
    Wait For Condition    Text    //body   contains    Discussion settings
    Check Checkbox    //input[@name="form.widgets.globally_enabled:list"]
    Click    //button[@name="form.buttons.save"]


# WHEN

I select '${content_type}' in types dropdown
    Select Options By    //select[@name="type_id"]    label    ${content_type}
    Wait For Condition    Text    //body   contains    Globally addable

Allow discussion
    Check Checkbox    //input[@name="allow_discussion:boolean"]
    Click    //button[@name="form.button.Save"]

I add new Link '${id}'
    Go to  ${PLONE_URL}
    Wait For Condition    Text    //body   contains    Plone site
    Create content
    ...    type=Link
    ...    id=${id}
    ...    title=${id}
    ...    remoteUrl=http://www.starzel.de


# THEN

Link '${id}' should have comments enabled
    Go to    ${PLONE_URL}/${id}
    Wait For Condition    Text    //body   contains    ${id}
    Get Element Count    //div[@id="commenting"]    should be    1

# Misc

Pause
    [Documentation]  Visually pause test execution with interactive dialog by
    ...              importing **Dialogs**-library and calling its
    ...              **Pause Execution**-keyword.
    Import library  Dialogs
    Pause execution