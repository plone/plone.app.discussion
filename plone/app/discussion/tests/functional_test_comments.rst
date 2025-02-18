======================
 plone.app.discussion
======================

This is a functional test for the plone.app.discussion comments viewlet.

We use zope.testbrowser to simulate browser interaction in order to show how
the plone.app.discussion commenting works.


Setting up and log in
---------------------

First we have to set up some things and login.

    >>> app = layer['app']
    >>> from plone.testing.zope import Browser
    >>> from plone.app.testing import SITE_OWNER_PASSWORD
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', f'Basic admin:{SITE_OWNER_PASSWORD}')
    >>> portal = layer['portal']
    >>> portal_url = 'http://nohost/plone'

By default, only HTTP error codes (e.g. 500 Server Side Error) are shown when an
error occurs on the server. To see more details, set handleErrors to False:

    >>> browser.handleErrors = False

We also keep another testbrowser handy for testing how tiles are rendered if
you're not logged in::

    >>> unprivileged_browser = Browser(app)
    >>> browser_member = Browser(app)
    >>> browser_user = Browser(app)
    >>> browser_reviewer = Browser(app)

Make sure we have a test user from the layer and it uses fancy characters:

    >>> from Products.CMFCore.utils import getToolByName
    >>> mtool = getToolByName(portal, 'portal_membership', None)
    >>> jim_fullname = mtool.getMemberById('jim').getProperty('fullname')
    >>> jim_fullname
    'Jim Fult\xc3\xb8rn'

Enable commenting.

    >>> from zope.component import queryUtility
    >>> from plone.registry.interfaces import IRegistry
    >>> from plone.app.discussion.interfaces import IDiscussionSettings
    >>> registry = queryUtility(IRegistry)
    >>> settings = registry.forInterface(IDiscussionSettings)
    >>> settings.globally_enabled = True

    >>> import transaction
    >>> transaction.commit()

Create a public page with comments allowed.

    >>> browser.open(portal['doc1'].absolute_url() + '/edit')
    >>> browser.getControl(name='form.widgets.IDublinCore.title').value = "Doc1"
    >>> browser.getControl(name='form.widgets.IAllowDiscussion.allow_discussion:list').value = ['True']
    >>> browser.getControl('Save').click()
    >>> urldoc1 = browser.url

Make sure the document is published:

    >>> browser.getLink("Publish").click()
    >>> 'Published' in browser.contents
    True

Check that the form has been properly submitted

    >>> browser.url
    'http://nohost/plone/doc1'


Comment Viewlet
---------------

Check that the old comments viewlet does not show up

    >>> 'discussion_reply_form' in browser.contents
    False

Check that the comment form/viewlet shows up

    >>> 'formfield-form-widgets-in_reply_to' in browser.contents
    True

    >>> 'formfield-form-widgets-comment-text' in browser.contents
    True


Post a comment as admin
-----------------------

Login as admin.

    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_NAME
    >>> setRoles(portal, 'manager', ['Manager'])

Post a comment as admin.

    >>> browser.getControl(name='form.widgets.text').value = "Comment from admin"
    >>> submit = browser.getControl(name='form.buttons.comment')
    >>> submit.click()

Check if comment has been added properly.

    >>> '<a href="http://nohost/plone/author/admin">admin</a>' in browser.contents
    True

    >>> "Comment from admin" in browser.contents
    True


Post a comment as user
----------------------

Login as user (without the 'Member' role).

    >>> browser_user.open(portal_url + '/login_form')
    >>> browser_user.getControl(name='__ac_name').value = 'johndoe'
    >>> browser_user.getControl(name='__ac_password').value = TEST_USER_PASSWORD
    >>> browser_user.getControl('Log in').click()

Users without the 'Reply to item' permission will not see the comment form,
because they don't have the 'Reply to item' permission. By default, this
permission is only granted to the 'Member' role.

    >>> 'form.widgets.text' in browser_user.contents
    False

    >>> 'form.buttons.comment' in browser_user.contents
    False


Post a comment as member
------------------------

Login as user 'jim'.
    >>> browser_member.open(portal_url + '/login_form')
    >>> browser_member.getControl(name='__ac_name').value = 'jim'
    >>> browser_member.getControl(name='__ac_password').value = TEST_USER_PASSWORD
    >>> browser_member.getControl('Log in').click()

Post a comment as user jim.

    >>> browser_member.open(urldoc1)
    >>> browser_member.getControl(name='form.widgets.text').value = "Comment from Jim"
    >>> submit = browser_member.getControl(name='form.buttons.comment')
    >>> submit.click()

Check if the comment has been added properly.

    >>> browser_member.contents
    '...<a href="http://nohost/plone/author/jim">Jim Fult\xc3\xb8rn</a>...'

    >>> "Comment from Jim" in browser_member.contents
    True


Post a comment as an anonymous user
-----------------------------------

Login and post comment as Anonymous

    >>> unprivileged_browser.open(urldoc1)

    >>> 'Log in to add comments' in unprivileged_browser.contents
    True

Enable anonymous comment

    >>> browser.open(portal_url + '/logout')
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'admin'
    >>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> browser.open(portal_url+'/@@discussion-controlpanel')
    >>> browser.getControl(name='form.widgets.anonymous_comments:list').value = 'selected'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> browser.open(portal_url + '/logout')

Now we can post an anonymous comment.

    >>> unprivileged_browser.open(urldoc1)
    >>> unprivileged_browser.getControl(name='form.widgets.text').value = "This is an anonymous comment"
    >>> unprivileged_browser.getControl(name='form.buttons.comment').click()

    >>> '<span>Anonymous</span>' in unprivileged_browser.contents
    True

    >>> 'This is an anonymous comment' in unprivileged_browser.contents
    True

Make sure special characters work as well.

    >>> unprivileged_browser.open(urldoc1)
    >>> tarek_fullname = "Tarek Ziadé"
    >>> unprivileged_browser.getControl(name='form.widgets.author_name').value = tarek_fullname
    >>> unprivileged_browser.getControl(name='form.widgets.text').value = "This is an äüö comment"
    >>> unprivileged_browser.getControl(name='form.buttons.comment').click()

    >>> tarek_fullname in unprivileged_browser.contents
    True

    >>> 'This is an äüö comment' in unprivileged_browser.contents
    True


Reply to an existing comment
----------------------------

Check that there is no existing direct reply to a comment.

    >>> 'replyTreeLevel1' in browser.contents
    False

Find a comment id to reply to.

    >>> browser.open(urldoc1)
    >>> import re
    >>> comment_div = re.findall('<div.*?.class="comment.*?>', browser.contents)[0]
    >>> id = re.findall('"([^"]*)"', comment_div)[1]

Post a reply to an existing comment.

    >>> browser.getControl(name='form.widgets.in_reply_to').value = id
    >>> browser.getControl(name='form.widgets.text').value = "Reply comment"
    >>> browser.getControl(name='form.buttons.comment').click()

Check that the reply has been posted properly.

    >>> 'Reply comment' in browser.contents
    True

    >>> 'level-1' in browser.contents
    True


Edit an existing comment
------------------------

Log in as admin

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl('Login Name').value = 'admin'
    >>> browser.getControl('Password').value = SITE_OWNER_PASSWORD
    >>> browser.getControl('Log in').click()

Use the Plone control panel to enable comment editing.

    >>> browser.open(portal_url + '/@@overview-controlpanel')
    >>> browser.getLink('Discussion').click()
    >>> browser.getControl('Enable editing of comments').selected = True
    >>> browser.getControl(name='form.buttons.save').click()

Extract the edit comment url from the first "edit comment" button

    >>> browser.open(urldoc1)
    >>> url = browser.getLink(url='@@edit-comment').url
    >>> '@@edit-comment' in url
    True

Open the edit comment view

    >>> browser.open(url)
    >>> ctrl = browser.getControl('Comment')
    >>> ctrl.value
    'Comment from admin'

Change and save the comment

    >>> ctrl.value = 'Comment from admin / was edited'
    >>> browser.getControl('Save').click()

This used to trigger permissions problems in some portlet configurations.
Check it ain't so.

    >>> 'require_login' in browser.url
    False
    >>> browser.url.startswith('http://nohost/plone/doc1')
    True
    >>> 'Comment from admin / was edited' in browser.contents
    True

Opening the edit comment view, then cancel, does nothing.

    >>> url = browser.getLink(url='@@edit-comment').url
    >>> '@@edit-comment' in url
    True
    >>> browser.open(url)
    >>> browser.getControl('Cancel').click()
    >>> browser.url.startswith('http://nohost/plone/doc1')
    True


Anon cannot edit comments.

    >>> unprivileged_browser.open(urldoc1)
    >>> '@@edit-comments' in browser.contents
    False

But Anon can see the edited comment.

    >>> 'Comment from admin / was edited' in unprivileged_browser.contents
    True


Deleting existing comments | 'Delete comments' permission
----------------------------------------------------------

Anonymous cannot delete comments

    >>> unprivileged_browser.open(urldoc1)
    >>> 'form.button.DeleteComment' in unprivileged_browser.contents
    False

A member cannot delete his own comments if he can't review or he isn't a Site Administrator

    >>> browser_member.open(urldoc1)
    >>> 'form.button.DeleteComment' in browser_member.contents
    False

Admin can delete comments

    >>> browser.open(urldoc1)
    >>> 'form.button.DeleteComment' in browser.contents
    True

Extract the delete comment url from the first "delete comment" button

    >>> browser.open(urldoc1)
    >>> form = browser.getForm(name='delete', index=0)
    >>> delete_url = form.action
    >>> '@@moderate-delete-comment' in delete_url
    True
    >>> comment_id = delete_url.split('/')[-2]

Anonymous cannot delete a comment by hitting the delete url directly.

    >>> unprivileged_browser.open(delete_url)

The comment is still there

    >>> unprivileged_browser.open(urldoc1)
    >>> comment_id in unprivileged_browser.contents
    True

A Member cannot delete even his own comment by hitting the delete url directly.

Extract the member comment id from the admin browser

    >>> form = browser.getForm(name='delete', index=2)
    >>> delete_url = form.action
    >>> '@@moderate-delete-comment' in delete_url
    True
    >>> comment_id = delete_url.split('/')[-2]

Now try to hit that url as the member owning that comment.
Work around some possible testbrowser breakage and check the result later.

    >>> try:
    ...   browser_member.open(delete_url)
    ... except:
    ...   pass

The comment is still there

    >>> browser_member.open(urldoc1)
    >>> comment_id in browser_member.contents
    True
    >>> 'Comment from Jim' in browser_member.contents
    True

Now login as user 'reviewer'

    >>> browser_reviewer.open(portal_url + '/login_form')
    >>> browser_reviewer.getControl(name='__ac_name').value = 'reviewer'
    >>> browser_reviewer.getControl(name='__ac_password').value = TEST_USER_PASSWORD
    >>> browser_reviewer.getControl('Log in').click()

Admin and who have 'Delete comments' permission (reviewers for example), can delete comments

    >>> browser_reviewer.open(urldoc1)
    >>> form = browser_reviewer.getForm(name='delete', index=0)
    >>> '@@moderate-delete-comment' in form.action
    True

    >>> comment_id = form.action.split('/')[-2]

Submitting the form runs into a testbrowser notFoundException.
We'll just catch that and check the result later.

    >>> try:
    ...   form.submit()
    ... except:
    ...   pass

Returning to the document we find the deleted comment is indeed gone

    >>> browser_reviewer.open(urldoc1)
    >>> comment_id in browser_reviewer.contents
    False


Post a comment with comment review workflow enabled
---------------------------------------------------

Enable the 'comment review workflow' for comments.

    >>> portal.portal_workflow.setChainForPortalTypes(('Discussion Item',), ('comment_review_workflow'),)
    >>> portal.portal_workflow.getChainForPortalType('Discussion Item')
    ('comment_review_workflow',)

We need to commit the transaction, otherwise setting the workflow will not work.

    >>> import transaction
    >>> transaction.commit()

Post comment as anonymous user.

    >>> unprivileged_browser.open(urldoc1)
    >>> unprivileged_browser.getControl(name='form.widgets.text').value = "Comment review workflow comment"
    >>> unprivileged_browser.getControl(name='form.buttons.comment').click()

Make sure the comment has not been published.

    >>> 'Comment review workflow comment' not in unprivileged_browser.contents
    True

Make sure the user gets a notification that the comment awaits moderator
approval.

    >>> 'Your comment awaits moderator approval' in unprivileged_browser.contents
    True


Edit the content object after a comment has been posted
-------------------------------------------------------

Make sure we still can edit the content object after a comment has been posted.
This is a regression test for http://dev.plone.org/plone/ticket/11157
(TypeError: Can't pickle objects in acquisition wrappers).

Login as admin.

    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'admin'
    >>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
    >>> browser.getControl('Log in').click()

Edit the content object.

    >>> from plone.protect.authenticator import _getKeyring
    >>> import hmac
    >>> from hashlib import sha1 as sha
    >>> ring = _getKeyring('foo')
    >>> secret = ring.random()
    >>> token = hmac.new(secret.encode('utf8'), b'admin', sha).hexdigest()
    >>> browser.open("http://nohost/plone/doc1/edit?_authenticator=" + token)
    >>> browser.getControl(name='form.widgets.IRichTextBehavior.text').value = "Lorem ipsum"
    >>> browser.getControl('Save').click()

Make sure the edit was successful.

    >>> 'Lorem ipsum' in browser.contents
    True


Require anonymous email
-----------------------

Edit the control panel.

    >>> browser.open(portal_url + '/logout')
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'admin'
    >>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> browser.open(portal_url+'/@@discussion-controlpanel')
    >>> browser.getControl(name='form.widgets.anonymous_email_enabled:list').value = 'selected'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> browser.open(portal_url + '/logout')

Post an anonymous comment without setting the email.

    >>> unprivileged_browser.open(urldoc1)
    >>> unprivileged_browser.getControl(name='form.widgets.text').value = "This is an anonymous comment without email"
    >>> unprivileged_browser.getControl(name='form.buttons.comment').click()
    >>> 'Required input is missing' in unprivileged_browser.contents
    True

Try again.

    >>> unprivileged_browser.getControl(name='form.widgets.text').value = "This is an anonymous comment with email"
    >>> unprivileged_browser.getControl(name='form.widgets.author_email').value = "email@example.org"
    >>> unprivileged_browser.getControl(name='form.buttons.comment').click()
    >>> 'Required input missing' in unprivileged_browser.contents
    False
    >>> 'Your comment awaits moderator approval' in unprivileged_browser.contents
    True

Email is being validated.

    >>> unprivileged_browser.getControl(name='form.widgets.text').value = "This is an anonymous comment with email"
    >>> unprivileged_browser.getControl(name='form.widgets.author_email').value = "abc"
    >>> unprivileged_browser.getControl(name='form.buttons.comment').click()
    >>> 'Invalid email address.' in unprivileged_browser.contents
    True
    >>> 'Your comment awaits moderator approval' in unprivileged_browser.contents
    False

Check again with valid email.

    >>> unprivileged_browser.getControl(name='form.widgets.text').value = "This is an anonymous comment with email"
    >>> unprivileged_browser.getControl(name='form.widgets.author_email').value = "email@example.org"
    >>> unprivileged_browser.getControl(name='form.buttons.comment').click()
    >>> 'Invalid email address.' in unprivileged_browser.contents
    False
    >>> 'Your comment awaits moderator approval' in unprivileged_browser.contents
    True


Posting as member should still work.  Especially it should not
complain about missing input for an invisible author_email field.
Login as user 'jim'.

    >>> browser_member.open(portal_url + '/login_form')
    >>> browser_member.getControl(name='__ac_name').value = 'jim'
    >>> browser_member.getControl(name='__ac_password').value = TEST_USER_PASSWORD
    >>> browser_member.getControl('Log in').click()

Post a comment as user jim.

    >>> browser_member.open(urldoc1)
    >>> browser_member.getControl(name='form.widgets.text').value = "Use the ZODB, Luke!"
    >>> submit = browser_member.getControl(name='form.buttons.comment')
    >>> submit.click()

Check if there are no validation errors.

    >>> 'Required input missing' in browser_member.contents
    False
    >>> 'Your comment awaits moderator approval' in browser_member.contents
    True
