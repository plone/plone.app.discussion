---
myst:
  html_meta:
    "description": "Howto extend the comment form with additional fields - plone.app.discussion documentation"
    "property=og:description": "Howto extend the comment form with additional fields - plone.app.discussion documentation"
    "property=og:title": "Howto extend the comment form with additional fields"
    "keywords": "Plone, Discussion, Comments, Documentation"
---

# Howto extend the comment form with additional fields

This document explains how to extend the plone.app.discussion comment form with
additional fields in an add-on product.

plone.app.discussion uses the
[plone.z3cform.fieldsets](http://pypi.python.org/pypi/plone.z3cform#fieldsets-and-form-extenders)
package which provides support for modifications via "extender" adapters. The
idea is that a third party component can modify the fields in a form and the
way that they are grouped and ordered.

:::{note}
This howto applies only to plone.app.discussion >= 2.0.4 and >= 1.1.2. Prior
versions will not store the extended fields on the comment.
:::

:::{seealso}
The source code of this howto can be found here:
<https://github.com/collective/example.commentextender/>
:::

## Howto extend the comment form with an additional "website" field

First, create a new plone package:

```
$ paster create -t plone example.commentextender
```

Go to the main directory of the package
(example.commentextender/example/commentextender) and create a new file
*commentextender.py*.

This file contains the ICommentExtenderFields interface definition with a
"website" field, a persistent CommentExtenderFields class to store the value of
the "website" field, a CommentExtenderFactory to create the
CommentExtenderFields, and a CommentExtender class to extend the default
comment form with the "website" field:

```
from persistent import Persistent

from z3c.form.field import Fields

from zope import interface
from zope import schema

from zope.annotation import factory
from zope.component import adapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from plone.z3cform.fieldsets import extensible

from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.comment import Comment

# Interface to define the fields we want to add to the comment form.
class ICommentExtenderFields(Interface):
    website = schema.TextLine(title="Website", required=False)

# Persistent class that implements the ICommentExtenderFields interface
@adapter(Comment)
class CommentExtenderFields(Persistent):
    interface.implements(ICommentExtenderFields)
    website = ""

# CommentExtenderFields factory
CommentExtenderFactory = factory(CommentExtenderFields)

# Extending the comment form with the fields defined in the
# ICommentExtenderFields interface.
@adapter(Interface, IDefaultBrowserLayer, CommentForm)
class CommentExtender(extensible.FormExtender):
    fields = Fields(ICommentExtenderFields)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def update(self):
        # Add the fields defined in ICommentExtenderFields to the form.
        self.add(ICommentExtenderFields, prefix="")
        # Move the website field to the top of the comment form.
        self.move('website', before='text', prefix="")
```

:::{seealso}
- See the plone.z3cform pypi page for more documentation about how to add,
  hide, and reorder fields:
  <http://pypi.python.org/pypi/plone.z3cform#fieldsets-and-form-extenders>
:::

Now register the CommentExtenderFactory and CommentExtender Classes that has
been created by adding the following lines to your configure.zcml:

```
<adapter
  factory=".commentextender.CommentExtenderFactory"
  provides=".commentextender.ICommentExtenderFields" />

<adapter
  factory=".commentextender.CommentExtender"
  provides="plone.z3cform.fieldsets.interfaces.IFormExtender" />
```

Create a new Plone instance, globally allow commenting, allow commenting on a
content object and you will see a comment form with an additional "website"
field.

Since we do not only want to store the "website" value on the comments, but also
to show these values for existing comments, we have to override the comments
viewlet. The easiest way to do this is to use z3c.jbot.

First, add [z3c.jbot](http://pypi.python.org/pypi/z3c.jbot). to the setup.py
of the example.commentextender package:

```
install_requires=[
    ...
    'z3c.jbot',
],
```

Next, create a new directory called "overrides" inside the
example.commentextender package and register it together with z3c.jbot in your
configure.zcml:

```
<configure
    ...
    xmlns:browser="http://namespaces.zope.org/browser">

  ...

  <include package="z3c.jbot" file="meta.zcml" />

  <browser:jbot
    directory="overrides" />

</configure>
```

Copy plone.app.discussion/plone/app/discussion/browser/comments.pt to the
overrides directory we just created and rename comments.pt to
plone.app.discussion.browser.comments.pt.

You can now add code to show the website attribute to the documentByLine:

```
<div class="documentByLine" i18n:domain="plone">
    ...
    <div class="commentWebsite"
         tal:condition="reply/website|nothing">
       <a href=""
          tal:attributes="href reply/website"
          tal:content="reply/website"></a>
    </div>
</div>
```

Restart your Plone instance and you will see the "website" field in the
documentByLine next to the comments.
