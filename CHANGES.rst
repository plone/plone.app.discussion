Changelog
=========

2.4.19 (2017-01-02)
-------------------

New features:

- Reindex comments when they are modified.
  [gforcada]


2.4.18 (2016-09-20)
-------------------

Bug fixes:

- Apply security hotfix 20160830 for redirects.  [maurits]

- Update Traditional Chinese translation.
  [l34marr]


2.4.17 (2016-08-17)
-------------------

Bug fixes:

- Use zope.interface decorator.
  [gforcada]


2.4.16 (2016-06-27)
-------------------

Bug fixes:

- Cleaned code from flake8 errors.  [maurits]

- Removed ``comment-migration`` view.  This did not work anymore on
  Plone 5.  If you still need to migrate from old-style comments, so
  from Plone 4.0 or earlier, please upgrade to Plone 4.3 first.
  [maurits]


2.4.15 (2016-06-12)
-------------------

Bug fixes:

- Reset the required setting of the author_email widget each time.
  Otherwise, the email field might get set to required when an
  anonymous user visits, and then remain required when an
  authenticated user visits, making it impossible for an authenticated
  user to fill in the form without validation error.  Or when in the
  control panel the field is set as not required anymore, that change
  would have no effect until the instance was restarted.  [maurits]


2.4.14 (2016-06-06)
-------------------

New features:

- Make tests work with lxml safe html cleaner

Bug fixes:

- Fixed possible cross site scripting (XSS) attack on moderate comments page.  [maurits]



2.4.13 (2016-05-04)
-------------------

Fixes:

- Removed docstrings from some methods to avoid publishing them.  From
  Products.PloneHotfix20160419.  [maurits]


2.4.12 (2016-04-13)
-------------------

Fixes:

- Mark 'Edit' button for translation.
  https://github.com/plone/plone.app.discussion/issues/90
  [gforcada]


2.4.11 (2016-03-31)
-------------------

New:

- For the discussion controlpanel, change base URLs from portal URL to what getSite returns, but don't change the controlpanels context binding.
  This allows for more flexibility when configuring it to be allowed on a sub site with a local registry.
  [thet]

Fixes:

- fixed translate translation plone-ru.po


2.4.10 (2016-02-08)
-------------------

New:

- Added russian translations.  [serge73]

Fixes:

- Get rid of the monkey patch on Products.CMFPlone's CatalogTool.
  Issue https://github.com/plone/Products.CMFPlone/issues/1332
  [staeff, fredvd]

- Cleanup code according to our style guide.
  [gforcada]


2.4.9 (2015-11-25)
------------------

Fixes:

- Update Site Setup link in all control panels (fixes https://github.com/plone/Products.CMFPlone/issues/1255)
  [davilima6]

- In tests, use ``selection.any`` in querystrings.
  Issue https://github.com/plone/Products.CMFPlone/issues/1040
  [maurits]

- Move translations to plone.app.locales
  https://github.com/plone/plone.app.discussion/issues/66
  [gforcada]


2.4.8 (2015-09-20)
------------------

- Use registry lookup for types_use_view_action_in_listings
  [esteele]

- Remove discussion.css
  [pbauer]

- Fix reply button not showing up since it uses a hide class which needs
  to be removed instead of a display value
  [ichim-david]


2.4.7 (2015-09-15)
------------------

- Tweak discussions.css styles to better live with plonetheme.barcelonata
  [ichim-david]


2.4.6 (2015-09-14)
------------------

- Fix editing comments in Plone 5.
  [pbauer]

- Move anonymous_email_enabled after anonymous_comments in controlpanel.
  [pbauer]


2.4.5 (2015-09-11)
------------------

- Updated basque translation
  [erral]


2.4.4 (2015-07-18)
------------------

- Change the category of the configlet to 'plone-general'.
  [sneridagh]

- Updated links for the renamed 'Types' control panel.
  [sneridagh]

- Updated Spanish translation.
  [Caballero]


2.4.3 (2015-06-05)
------------------

- Update Spanish translation.
  [macagua]

- Only use edit overlay if available for editing comments
  [vangheem]


2.4.2 (2015-05-04)
------------------

- Update Japanese translation.
  [takanory]
- Update Japanese translation.
  [terapyon]

- Sort imports as per plone.api styleguide.
  [gforcada]

- Fix flake8 errors reported by jenkins.plone.org.
  [gforcada]


2.4.1 (2015-03-26)
------------------

- i18n for ICaptcha interface.
  [davidjb]


2.4.0 (2015-03-12)
------------------

- use requirejs if available
  [vangheem]

- Rename @@discussion-settings to @@discussion-controlpanel
  [maartenkling]

- Add permission to allow comment authors to delete their own comments if
  there are no replies yet.
  [gaudenz]

- Updated portuguese pt-br translation.
  [jtmolon]

- Read mail settings from new (Plone 5) registry.
  [timo]

- Remove @property from Conversation.total_comments as @property and
  Acquisition don't play well together.
  [gforcada]


2.3.3 (2014-10-23)
------------------

- Don't execute createReplyForm js if there is no in_reply_to button.
  [vincentfretin]

- Register events as Content Rules Event Types if plone.contentrules is present
  [avoinea]

- Trigger custom events on comment add/remove/reply
  [avoinea]

- Replace $.live with $.on for jQuery >= 1.9 compatibility. This works on
  jQuery >= 1.7 (Plone 4.3 onwards).
  [gaudenz]

- Update Traditional Chinese translations.
  [marr]

- Make comments editable.
  [pjstevns, gyst]

- Provide 'Delete comments' permission to handle comments deletion
  [cekk]

- Fixed Italian translations [cekk]


2.3.2 (2014-04-05)
------------------

- bugfix: according to IDiscussionSettings.anonymous_email_enabled (cite):
  "If selected, anonymous user will have to give their email." - But field
  was not required. Now it is.
  [jensens]

- bugfix: anonymous email field was never saved.
  [jensens]

- updated german translations: added some missing msgstr.
  [jensens]

- added i18ndude and a script ``update_translations`` to buildout in order
  to make translation updates simpler.
  [jensens]

- Fix reindexObject for content_object in moderation views.
  Now reindex only "total_comments" index and not all the indexes
  [cekk]

- Fix comments Title if utf-8 characters in author_name
  [huub_bouma]

- use member.getId as author_username, so membrane users having different id
  then username still have there picture shown and author path is correct.
  [maartenkling]


2.3.1 (2014-02-22)
------------------

- 2.3.0 was a brown bag release.
  [timo]


2.3.0 (2014-02-22)
------------------

- Remove DL's from portal message in templates.
  https://github.com/plone/Products.CMFPlone/issues/153
  [khink]

- Execute the proper workflow change when using the moderation buttons instead
  of hardcoding the workflow action to always publish
  [omiron]

- Corrections and additions to the Danish translation
  [aputtu]


2.2.12 (2014-01-13)
-------------------

- Show author email to Moderator when it is available in anonymous comment.
  [gotcha, smoussiaux]

- Put defaultUser.png instead of old defaultUser.gif
  [bsuttor]

- Remove bbb directory. bbb was never really implemented.
  [timo]

- Replace deprecated test assert statements.
  [timo]

- Remove portal_discussion tool.
  [timo]

- Refactor tests to use the PLONE_APP_CONTENTTYPES_FIXTURE instead of
  PLONE_FIXTURE.
  [timo]

- Fix ownership of comments.
  [toutpt]


2.2.10 (2013-09-24)
-------------------

- Revert "Refactor tests to use the PLONE_APP_CONTENTTYPES_FIXTURE instead of
  the PLONE_FIXTURE." that has been accidentially introduced into the 2.2.9
  release.
  [timo]


2.2.9 (2013-09-24)
------------------

- Portuguese translation added.
  [Rui Silva]

- Rename CHANGES.txt to CHANGES.rst.
  [timo]

- Fix ajax form submit for delete comment action: add 'data' to the request.
  [toutpt]


2.2.8 (2013-08-20)
------------------

- Re-release 2.2.7 with .mo files. Seems like 2.2.7 has been released twice on
  two different dates. The first release seems to be made without a github
  push.
  [timo]

- Fix comments viewlet's get_replies for non-annotatable objects.
  [witsch]


2.2.7 (2013-07-04)
------------------

- making sure .mo files are present at release
  [garbas]

- Revert change that silently added mime_type attribute values
  to old discussion items that had none.
  [pjstevns]


2.2.6 (2013-05-23)
------------------

- Fix migration to not fail when member has been deleted.
  [datakurre]


2.2.5 (2013-04-06)
------------------

- Update pt_BR translation [ericof]

- Do not raise an error when no workflow is assigned to the comment type.
  [timo]

- Add a conversation property public_commentators that only lists
  commentators of comments that are public.
  The commentators indexer indexes this field now.
  The behavior of the conversation property commentators is
  unchanged.
  [do3cc]

- The last comment date now only returns the date of the newest
  published comment.
  [do3cc]


2.2.4 (2013-03-05)
------------------

- Check for 'checked' attribute in a way that work also for jQuery 1.7
  [ichimdav]

- Better fix for #13037 by removing submit event trigger altogether
  [ichimdav]

- Added Romanian translation
  [ichimdav]

- Updated Ukrainian translation
  [kroman0]


2.2.3 (2013-01-13)
------------------

- add anonymous_email_enabled settings to really let integrator activate
  the email field on comment add form when anonymous.
  [toutpt]


2.2.2 (2012-11-16)
------------------

- first check if captcha is installed before we open browsers zcml
  files that depend on these packages, fixes #12118 and #12774
  [maartenkling]


2.2.1 (2012-11-16)
------------------

- Make conversation view not break when comment-id cannot be converted to
  long. This fixes #13327
  [khink]

- fix insufficient privileges when trying to view
  the RSS feed of a comment collection
  [maartenkling]

- removed inline border=0 and move it to css
  [maartenkling]

- For migrations of comments without a valid old_status, apply the 'published'
  state.
  [thet]

- Re-apply eleddy's "Revert modification date since this is fixed in
  p.a.caching now." as her commit was lost later on due to some git magic.
  [thet]

- Remove submitting the controlpanel form again after removing disabled tags
  fixes #13037 and #12357
  [maartenkling]

- Remove inline styles, fixes #12399
  [maartenkling]

- add fallback border color for i8, fixes #11324
  [maartenkling]

- Replace discussionitem_icon.gif with png version.
  [timo]

- Fix catalog updates for IObjectMovedEvent
  [gaudenz]

- Fix non-functioning user_notification feature
  [izak]


2.2.0 (2012-08-30)
------------------

- Refactor the comment creator/author_name to comply with the Plone core
  convention to store the username on the creator attribute and not the
  fullname.
  [timo]

- Rename the id of the text widgets because there can be css-id clashes with
  the text field of documents when using TinyMCE in overlays or multiple
  instances of TinyMCE on a single page.
  [timo]

- text/html added to the possible mime types for comments.
  [timo]

- Make 'text/plain' the default mime type for comments and make sure the
  default type is set properly when creating a new comment.
  [timo]

- Fix handling of comments with invalid transforms. Write an error msg
  to the log and just return the untransformed text.
  [timo]


2.1.8 (unreleased)
------------------

- Support for Dexterity added. The conversation enabled method now detects and
  supports Dexterity-based content types.
  [timo]

- No more recursive came_from redirection after logged_in.
  [kcleong, huubbouma]

- Danish translation updated.
  [stonor]

- Documentation and howtos updated.
  [timo]

- Remove development buildout files and directories.
  [timo]


2.1.7 (2012-06-29)
------------------

- Prune duplicated test code.
  [pjstevns]

- Update version in buildout.cfg to allow development.
  [pjstevns]

- Conversation.total_comments only counts published comments.
  Fixes bug #11591.
  [pjstevns]

- Set workflow status of comments during migration based on
  the state of the Discussion Item.
  [pjstevns]


2.1.6 (2012-05-30)
------------------

- Add Site Administrator role to Review comments permission.
  [gaudenz]

- Fix excessive JS comment deletion.
  [gaudenz]

- Hide Conversation objects from breadcrumb navigation. The breadcrumbs
  navigation is also used in the search results view. This lead to Conversation
  objects showing up if 'Discussion Items' are searchable.
  [gaudenz]

- No longer depend on zope.app packages.
  [hannosch]


2.1.5 (2012-04-05)
------------------

- Redirect to "/view" for Image, File and anything listed as requiring
  a view in the url to properly display comments.
  [eleddy]

- Make comments and controlpanel views more robust, so they don't break if no
  workflow is assigned to the 'Discussion Item' content type.
  [timo]

- Warning message added to discussion control panel that shows up if there are
  unmigrated comments.
  [timo]

- Make topic/collection tests pass when plone.app.collection is installed.
  [timo]


2.1.4 (2012-02-29)
------------------

- Revert modification date since this is fixed in p.a.caching now.
  [eleddy]

- Add missing meta_typ to "Review comments" portal action.
  [batlock666]


2.1.3 (2012-01-24)
------------------

- Set modified date of object receiving comments so that caching works
  correctly (304s)
  [eleddy]


2.1.2 (2011-12-21)
------------------

- Fixed language code error in Ukrainian translation. The message
  catalog was erroneously set to "English".
  [chervol]

- Do not raise an error if the comment text is None.
  [timo]

- Updated Spanish translation.
  [hvelarde]

- Fix that catalog rebuild breaks the path attribute on comments. This fixes
  http://dev.plone.org/ticket/12437.
  [pjstevns]


2.1.1 (2011-11-24)
------------------

- Include mo files in the distribution.
  [vincentfretin]

- Fix various text typos.
  [timo]

- Fix control panel help text typos.
  [jonstahl]

- Documentation about overriding the comments viewlet js added.
  [timo]

- Corrected location of Japanese po file.
  [tyam]


2.1.0 (2011-08-22)
------------------

- Avoid error when moving objects that are contentish but not annotatable.
  [davisagli]

- New feature: Markdown syntax added to possible comment text transforms.
  [timo]

- Make sure the comment brains are updated properly when the content object is
  renamed.
  [hannosch, timo]

- Make sure only comments to the content object are removed from the catalog
  when the content object is moved.
  [hannosch, timo, davisagli]

- Make sure the conversation.getComments method returns acquisition wrapped
  comments.
  [timo]

- Ukrainian translation added.
  [chervol]

- Remove one_state_workflow customizations.
  [timo]


2.0.9 (2011-07-25)
------------------

- Make sure the creator index always stores utf-8 encoded stings and not
  unicode.
  [timo]


2.0.8 (2011-07-25)
------------------

- Automatically reload batch moderation page if no comments are left. This
  fixes http://dev.plone.org/plone/ticket/11298.
  [timo]

- Use Plone's safe_encode method instead of encode() for the creator index to
  make sure unicode encoded strings can be indexed too.
  [timo]


2.0.7 (2011-07-15)
------------------

- Fix discussion control panel submit for Google Chrome. This fixes
  http://dev.plone.org/plone/ticket/11486.


2.0.6 (2011-07-04)
------------------

- Update comment brains in zcatalog when moving a content object with comments.
  This fixes http://dev.plone.org/plone/ticket/11331.
  [timo]

- Plone 3 specific exclusion of plone.app.uuid removed.
  [timo]


2.0.5 (2011-06-16)
------------------

- Simplify CSS and JS registrations. CSS will now be imported using the
  standard link and so can be merged, inserted after forms.css. JS will now be
  imported after collapsibleformfields.js.
  [elro]

- Enable the left-menu on the configlet, to be more consistent with all other
  configlets. Related to http://dev.plone.org/plone/ticket/11737
  [WouterVH]

- Do not render/update the comment form in CommentViewlets if commenting is
  disabled, since this slows down the page rendering. This fixes
  http://dev.plone.org/plone/ticket/11930
  [fafhrd]


2.0.4 (2011-05-28)
------------------

- Refactor/clean up the handleComment method.
  [timo]

- Make handleComment method store comment attributes from form extenders. This
  allows us to extend the comment form with external add-ons. See
  http://packages.python.org/plone.app.discussion/howtos/howto_extend_the_comment_form.html
  for details.
  [timo]


2.0.3 (2011-06-19)
------------------

- Updated Simplified Chinese translation
  [jianaijun]

- Italian translation review.
  [gborelli]


2.0.2 (2011-05-12)
------------------

- Moderation should be enabled only if there is a workflow set for Discussion
  Item.
  [erico_andrei]


2.0.1 (2011-04-22)
------------------

- Translations updated. German translations for notifications added.
  [timo]

- Add links to delete/approve a comment in the moderator notification email.
  [timo]

- Remove the unnecessary workflow_action parameter from the PublishComments
  request.
  [timo]

- Make sure the email settings in the control panel are disabled when commenting
  is disabled globally.
  [timo]

- Enable/disable moderator_email setting dynamically as mail settings or
  discussion settings change.
  [timo]

- Remove ImportError exceptions for Plone < 4.1 code and plone.z3cform < 0.6.0.
  [timo]

- Provide the comment body text in the email notification.
  [timo]

- Fix comment link in email notification. This fixes
  http://dev.plone.org/plone/ticket/11413.
  [timo]

- Redirect to the comment itself when notifying a user about a new comment.
  [timo]


2.0 (2011-04-21)
----------------

- No changes.


2.0b2 (2011-04-21)
------------------

- Added Japanese translation.
  [tyam]

- Move all tests from testing layer to plone.app.testing.
  [timo]

- Move some policy out of the conversation storage adapter into a
  view, specifically "enabled()".  Prevents having to replace/migrate
  persistent objects to change policy which really only concerns the
  context and possibly the request, not the conversation storage.
  Fixes #11372.
  [rossp]

- Fix unindexing of comments when deleting content resulting from
  iterating over a BTree while modifying it. Fixes #11402.
  [rossp]

- Fix Missing.Value for Creator in the catalog. Fixes #11634.
  [rossp]

- Don't add the annotation unless a comment is actually being added.
  Fixes #11370.
  [rossp]

- Fixed i18n of the "Commenting has been disabled." message.
  [vincentfretin]

- Add a moderator_email setting to control where moderator notifications are
  sent.
  [davisagli]


2.0b1 (2011-04-06)
------------------

- Make discussion.css cacheable when registering it.
  [davisagli]

- Fix issue where GMT datetimes were converted into local timezone DateTimes
  during indexing.
  [davisagli]

- Handle timezones correctly while converting dates during the migration of
  legacy comments.
  [davisagli]

- When returning a comment's title, give preference to its title attribute
  if set.
  [davisagli]

- Use the cooked text of legacy comments when migrating.
  [davisagli]

- Make sure that comment text is transformed to plain text when indexing.
  [davisagli]

- Move logic for transforming comment text to the Comment class's getText
  method. Use a comment instance's mime_type attribute in preference to the
  global setting for the source mimetype. Use text/x-html-safe as the target
  mimetype to make sure the safe HTML filter is applied, in case the source is
  untrusted HTML.
  [davisagli]

- Provide a filter_callback option to the migration view, so that a custom
  policy for which comments get migrated can be implemented.
  [davisagli]

- Fixed RoleManager import to avoid deprecation warning on Zope 2.13.
  [davisagli]

- French translations.
  [thomasdesvenain]

- Fixed internationalization issues.
  [thomasdesvenain]

- Added Afrikaans translations
  [jcbrand]


2.0a3 (2011-03-02)
------------------

- Fixed test failure for the default user portrait, which changed from
  defaultUser.gif to defaultUser.png in Products.PlonePAS 4.0.5
  [maurits]


2.0a2 (2011-02-08)
------------------

- Fixed test failure for the default user portrait, which changed from
  defaultUser.gif to defaultUser.png in Products.PlonePAS 4.0.5.
  [maurits]

- Remove "Plone 3 only" code.
  [timo]

- Do not monkey patch the BAD_TYPES vocabulary or plone.app.vocabularies
  anymore.
  [timo]


2.0a1 (2011-02-07)
------------------

- Split up development into two branches. The 1.x branch will be for Plone 3.x
  and Plone 4.0.x and the 2.x branch will be for Plone 4.1 and beyond.
  [timo]

- Import Owned from OFS.owner to avoid deprecation warnings.
  [timo]

- Disable discussion by default.
  [timo]

- Enable ajaxify comment deletion again ([thomasdesvenain]). This has been
  disabled in 1.0b12 because of problems with Plone 3.
  [timo]

- Remove collective.autopermission dependency that has become unnecessary in
  Plone 4.1.
  [timo]


1.0 (2011-02-07)
----------------

- Do not check for a comment review workflow when sending out a moderator email
  notification. This fixes http://dev.plone.org/plone/ticket/11444.
  [timo]

- Check if the current user has configured an e-mail address for the email
  notification option. This fixes http://dev.plone.org/plone/ticket/11428.
  [timo]


1.0RC2 (2011-01-24)
-------------------

- Remove moderation_enabled setting from registry to avoid migration problems
  to 1.0RC1. This fixes http://dev.plone.org/plone/ticket/11419.
  [timo]


1.0RC1 (2011-01-22)
-------------------

- Always show existing comments, even if commenting is disabled.
  [timo]

- Fix CSS for commenter images with a width of more than 2.5em. This fixes
  http://dev.plone.org/plone/ticket/11391.
  [timo]

- Show a 'Comments are moderated.' message next to the comment form if comments
  are moderated.
  [timo]

- Make sure plone.app.registry's ZCML is loaded, so that its import step will run
  when plone.app.discussion is installed.
  [davisagli]

- Avoid sending multiple notification emails to the same person when
  he has commented multiple times.
  [maurits]

- Move discussion action item from actionicons.xml to actions.xml to avoid
  deprecation warning.
  [timo]

- Fix cancel button on edit view when using Dexterity types. This fixes
  http://dev.plone.org/plone/ticket/11338.
  [EpeliJYU]

- Assigning the 'Reply to item' permission to the 'Authenticated' role. The old
  commenting system allowed 'Authenticated' users to post comments. Also, OpenID
  users do not possess the 'Authenticated' role.
  [timo]

- Make sure the handleComment method checks for the 'Reply to item' permission
  when adding a comment.
  [timo]

- Make the mail-setting warning message show up in the discussion control panel.
  [timo]

- Link directly to the "Discussion Item" types control panel in the moderation
  view.
  [timo]

- Show "moderate comments" link in the admin panel only if a moderation
  workflow is enabled for comments.
  [timo]

- Do not allow to change the mail settings in the discussion control panel, if
  there is no valid mail setup.
  [timo]

- Disable all commenting options in the discussion control panel if comments
  are disabled globally.

- Check for the 'review comments' permission instead of 'manage' to decide
  if the user should see a 'this comment is pending' message.
  [timo]

- Move "moderate comments" site action above the logout action.
  [timo]

- Moderator notification description updated.
  [timo]

- Redirect back to the discussion control panel when the discussion control
  panel form is submitted.
  [timo]

- Fix document_byline bottom margin if commenter images are disabled.
  [timo]

- Dynamically show the comment formatting message dependent on the text
  transform setting.
  [timo]

- Description for text transform added to the discussion control panel.
  [timo]

- Move the discussion control panel to the core Plone configuration.
  [timo]

- Always set the effective date of a comment to the same value as the creation
  date.
  [timo]

- Fix SMTP exception when an email is send to the moderator.
  [timo]

- Make sure comment UIDs in the catalog are always unique. This fixes
  http://dev.plone.org/plone/ticket/10652.
  [timo]

- Fix 'check all' on batch moderation page.
  [davisagli]

- Use safe_unicode to decode the title of the content. encode("utf-9") caused
  Dexterity based content types to raise a unicode decode error. This fixes
  http://dev.plone.org/plone/ticket/11292
  [dukebody]

- Spanish translation updated.
  [dukebody]

- Catalan translation added.
  [sneridagh]

- Convert anonymous-supplied name to unicode as done for authenticated members.
  [ggozad]

- Catch SMTP exceptions when sending email notifications.
  [timo]

- Updated italian translation.
  [keul]


1.0b12 (2010-11-04)
-------------------

- Remove AJAX comment deletion binding. This function relies on the nextUntil()
  selector introduced by jQuery 1.4 and therefore breaks in Plone 3
  (that currently uses jQuery 1.3.2).
  [timo]


1.0b11 (2010-11-03)
-------------------

- Fix Dutch and Czech language code and name.
  [timo]

- Re-add the CommentsViewlet can_manage method. This method has been removed
  in version 1.0b9 and added again in 1.0b11 because we don't want to change
  the API in beta releases.
  [timo]

- Declare z3c.form and zope.schema as minimum version dependencies in setup.py
  in case people use a different KGS.
  [timo]

- Add and update es and eu l10ns.
  [dukebody, on behalf of erral]

- Ajaxify comment deletion and approval.
  [thomasdesvenain]

- New feature: As a logged-in user, I can enable/disable email notification of
  additional comments on this content object.
  [timo]

- Disable the plone.app.registry check on schema elements, so no error is
  raised on upgrades. This fixes http://dev.plone.org/plone/ticket/11195.
  [timo]

- Remove the too generic id attribute of the comment form.
  [timo]

- Fixed handling of non-ascii member data, like fullname and email.
  [hannosch]


1.0b10 (2010-10-15)
-------------------

- Fixed "global name 'WrongCaptchaCode' is not defined" if norobots captcha,
  but no other validation package is installed.
  [naro]

- Check if there is a 'pending' review state in the current workflow for
  comments instead of just checking for the 'comment_review_workflow'. This
  allows integrators to use a custom review workflow. This fixes
  http://dev.plone.org/plone/ticket/11184.
  [timo]

- fixed plone-it.po (improper language code ('en' instead of 'it'))
  [ajung]


1.0b9 (2010-10-07)
------------------

- Replace the can_manage method with a can_review method that checks the
  'Review comments' permission. This fixes
  http://dev.plone.org/plone/ticket/11145.
  [timo]

- Fix moderation actions (publish, delete) in the moderation view with virtual
  hosts. This is a replacement for http://dev.plone.org/plone/changeset/35608.
  [timo]

- Do not show two "login to add comments" buttons when there are no comments
  yet. This fixes http://plone.org/products/plone.app.discussion/issues/12.
  [timo]


1.0b8 (2010-10-04)
------------------

- Apply the comment viewlet template and styles to the new title-less comments.
  This might require integrators to apply their custom templates and styles.
  [timo]

- Remove title field from the comment form and replace it with an auto-generated
  title ("John Doe on Welcome to Plone").
  [timo]

- Fix http://dev.plone.org/plone/ticket/11098: "Comment byline shows login
  name, not full name"
  [kiorky]

- Make sure the __parent__ pointer (the conversation) of a comment is not
  acquisition wrapped in conversation.addComment. This fixes
  http://dev.plone.org/plone/ticket/11157.
  [timo]

- Revert r35608 since this was breaking the comment moderation bulk actions.
  The BulkActionsView expects the absolute path of the comments without the
  portal url (e.g. '/plone/doc1/++conversation++default/1285346769126020').
  This fixes http://dev.plone.org/plone/ticket/11156.
  [timo]

- Use "(function($) { /* some code that uses $ \*/ })(jQuery)" instead of
  "$(document).ready(function(){ /* some code that uses $ \*/ });" to invoke
  jQuery code.
  [timo]

- Finnish translation added.
  [saffe]

- Italian translation updated.
  [keul]


1.0b7 (2010-09-15)
------------------

* Captcha plugin support for collective.z3cform.norobots (version >= 1.1) added.
  [saffe]

* Store dates in utc and not in local time. Display local time
  [do3cc]

* Fetch context for the comment view with "context = aq_inner(self.context)".
  [timo]

* Raise an unauthorized error when authenticated users try to post a comment
  on a content object that has discussion disabled. Thanks to vincentfrentin
  for reporting this.
  [timo]

* Czech translation added.
  [naro]

* Clean up code with PyLint.
  [timo]

* Make Javascripts pass JSLint validation.
  [timo]

* Put email notification subscribers into their own zcml file so it is easier
  for integrators to override them.
  [timo]

* Plain text and intelligent text options for comment text added to preserve
  basic text structure and to make links clickable.
  [timo]

* Rewrote all tal:condition in comments.pt. The authenticated user has
  the reply button and the comment form if he has the "Reply to item"
  permission And the discussion is currently allowed.
  [vincentfretin]


1.0b6 (2010-08-24)
------------------

* Fixed the case where a folder has allow_discussion=False and
  conversation.enabled() on a document in this folder returned False
  instead of True because of allow_discussion acquisition.
  [vincentfretin]

* Redirect to the comment form action instead of the absolute URL when a
  comment is posted. This fixes the accidentally triggered file upload when a
  comment is posted on a file content object.
  [timo]

* We need five:registerPackage to register the i18n folder.
  [vincentfretin]

* Added Traditional Chinese (zh_TW) translation.
  [TsungWei Hu]

* Added French translation.
  [vincentfretin]

* Renamed legend_add_comment to label_add_comment to have the translation from
  plone domain.
  [vincentfretin]

* label_comment_by and label_commented_at are not in Plone 4 translation
  anymore, so these two messages moved to plone.app.discussions i18n domain.
  [vincentfretin]

* Translate "Warning" shown in @@moderate-comments in the plone domain.
  [vincentfretin]

* Fixed i18n markup of message_moderation_disabled.
  [vincentfretin]

* Catch Type errors in indexers if object can not be adapted to IDiscussion
  [do3cc]

* Call the CaptchaValidator even when no captcha data was submitted. This is
  necessary to ensure that the collective.akismet validator is called when
  installed.
  [timo]

* Spanish translation added. Thanks to Judith Sanleandro.
  [timo]


1.0b5 (2010-07-16)
------------------

* Use self.form instead of CommentForm for the CommentsViewlet update method so
  integrators don't have to override the viewlet's update method.
  [matous]

* Make sure the form fields in the reply form are always placed under the field
  labels.
  [timo]

* Fix CSS overflow bug that occurs with the new Plone 4.0b5 comment styles.
  [timo]

* Unnecessary imports and variables removed.
  [timo]

* Added norwegian translation.
  [ggozad]

* Protect against missing canonical in conversationCanonicalAdapterFactory.
  [hannosch]

* Documentation for Captcha plugin architecture and email notification added.
  See http://packages.python.org/plone.app.discussion.
  [timo]

* Use sphinx.plonetheme for plone.app.discussion documentation.
  [timo]

* Avoid deprecation warning for the Globals package.
  [hannosch]

* Remove the hard coded check for title and text when the comment form is
  submitted. This allows integrators to write schema extenders that remove the
  title from the comment form.
  [timo]

* Move captcha registration to its own captcha.zcml file.
  [timo]

* Akismet (http://akismet.com/) spam protection plugin (collective.akismet)
  support added.
  [timo]

* Simplify the CaptchaValidator class by dynamically adapting a view with the
  name of the captcha plugin (e.g. recaptcha, captcha, akismet) for the
  validator.
  [timo]

* Dutch translation added.
  [kcleong]

* Enable caching and merging for comments.js to save some requests.
  [pelle]

* Design notes for the Captcha plugin architecture added.
  [timo]

* Make IDiscussionLayer inherit from Interface again. Remove IDefaultPloneLayer,
  since Plone 4.0b1 and plone.theme 2.0b1 are out now.
  [timo]

* Clean up Javascript code.
  [timo]

* Fix encoding error in migration procedure, otherwise migration procedure
  breaks on joining output list in case we have there any non-ascii characters.
  [piv]

* plone.z3cform 0.6.0 compatibility (fix maximum recursion depth error which
  appears with plone.z3cform higher than 0.5.10).
  [piv]

* Removed moderation.js from js registry and include it only in moderation.pt as
  that is the only place where it is used.
  [ggozad]


1.0b4 (2010-04-04)
------------------

* New feature: As a moderator, I am notified when new comments require my
  attention.
  [timo]

* Sphinx-based developer documentation added. See
  http://packages.python.org/plone.app.discussion.
  [timo]

* Rename "Single State Workflow" to "Comment Single State Workflow".
  [timo]

* Rename 'publish comment' to 'approve comment'. This fixes #1608470.
  [timo]

* Show a warning in the moderation view if the moderation workflow is disabled.
  [timo]

* Move 'Moderate comments' link from site actions to user actions.
  [timo]

* Fix #662654: As an administrator, I can configure a Collection to show recent
  comments. Comment.Type() now correctly returns the FTI title ('Comment')
  [chaoflow]

* German translation updated.
  [juh]

* Fix #2419342: Fix untranslated published/deleted status messages.
  [timo]

* Remove fixed width of the actions column of the moderation view. The
  translated button titles can differ in size from the English titles.
  [timo]

* Fix #2494228: Remove comments as well when a content object is deleted.
  [timo]

* Fix unicode error when non-ASCII characters are typed into the name field of a
  comment by anonymous users.
  [regebro]

* Make p.a.d. work with the recent version of plone.z3cform (0.5.10)
  [timo]

* Make p.a.d. styles less generic. This fixes #10253.
  [timo]

* Added greek translation.
  [ggozad]

* A bug in the moderator panel meant you couldn't delete items in a virtual
  host, if your portal was named "plone".
  [regebro]


1.0b3 (2010-01-28)
------------------

* Added an i18n directory for messages in the plone domain and updated scripts
  to rebuild and sync it.
  [hannosch]

* Added an optional conversationCanonicalAdapterFactory showing how to share
  comments across all translations with LinguaPlone, by storing and retrieving
  the conversation from the canonical object.
  [hannosch]

* Play by the Plone 3.3+ rules and use the INavigationRoot as a base for the
  moderation view.
  [hannosch]

* Added a commentTitle CSS class to the comment titles.
  [hannosch]

* Update message ids to match their real text.
  [hannosch]

* Set CSS classes for the comment form in the updateActions method.
  [timo]

* Respect the allow_comments field on an object and avoid calculations if no
  comments should be shown.
  [hannosch]

* Automatically load the ZCML files of the captcha widgets if they are
  installed.
  [hannosch]

* Fixed i18n domain in GenericSetup profiles to be ``plone``. Other values
  aren't supported for GS profiles.
  [hannosch]

* Provide our own copy of the default one state workflow. Not all Plone sites
  have this workflow installed.
  [hannosch]

* Register the event subscribers for the correct interfaces in Plone 3.
  [hannosch]

* Factored out subscriber declarations into its own ZCML file.
  [hannosch]

* Bugfix for #2281226: Moderation View: Comments disappear when hitting the
  'Apply' button without choosing a bulk action.
  [timo]

* Allow to show the full text of a comment in the moderation view.
  [timo]

* German translation added.
  [timo]

* Italian translation added.
  [keul]


1.0b2 (2010-01-22)
------------------

* Bugfix for #2010181: The name of a commenter who commented while not logged in
  should not appear as a link.
  [timo]

* Bugfix for #2010078: Comments that await moderation are visually distinguished
  from published comments.
  [timo]

* Bugfix for #2010085: Use object_provides instead of portal_type to query the
  catalog for comment.
  [timo]

* Bugfix for #2010071: p.a.d. works with plone.z3cform 0.5.7 and
  plone.app.z3cform 0.4.9 now.
  [timo]

* Bugfix for #1513398: Show "anonymous" when name field is empty in comment
  form.
  [timo]

* Migration view: Dry run option added, abort transaction when something goes
  wrong during migration, be more verbose about errors.
  [timo]


1.0b1 (2009-12-08)
------------------

* Fix redirect after a adding a comment
  [timo]

* Replace yes/no widgets with check boxes in the discussion control panel
  [timo]

* Make comments viewlet show up in Plone 4
  [timo]

* Apply Plone 4 styles to comment form
  [timo]

* Simplify moderation view by removing the filters
  [timo]


1.0a2 (2009-10-18)
------------------

* Plone 4 / Zope 2.12 support
  [timo]

* Comment migration script added
  [timo]

* Pluggable plone.z3cform comment forms
  [timo]

* Captcha and ReCaptcha support added
  [timo]


1.0a1 (2009-06-07)
------------------

* Basic commenting functionality and batch moderation.
  [timo]
