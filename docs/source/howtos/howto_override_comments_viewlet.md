---
myst:
  html_meta:
    "description": "How to override plone.app.discussion's comments viewlet - plone.app.discussion documentation"
    "property=og:description": "How to override plone.app.discussion's comments viewlet - plone.app.discussion documentation"
    "property=og:title": "How to override plone.app.discussion's comments viewlet"
    "keywords": "Plone, Discussion, Comments, Documentation"
---

# How to override plone.app.discussion's comments viewlet

This document explains how to override the plone.app.discussion comments
viewlet that controls the way existing comments are displayed.

There are three different ways to override plone.app.discussion's comments
viewlet: through-the-web, on the file system with z3c.jbot, and by overriding
the comments viewlet class on the file system.

Overriding the comments viewlet template throught-the-web is the quick and
dirty approach. Using z3c.jbot is the recommended approach if you just want to
override the comments viewlet template. If you want full control over the
comments viewlet class, for instance if you want to add/customize view methods,
overriding the comments viewlet class on the file system is the recommended
approach.

## Override the comments template through-the web

Overriding the comments template through-the web is the easiest way to
customize the comments viewlet:

```
* Go to the ZMI (http://localhost:8080/Plone/manage_main)
* Click on "portal_view_customizations"
* Customize plone.comments (plone.app.discussion.interfaces.IDiscussionLayer)
```

## Override the comments template with z3c.jbot on the file system

The easiest way to override the comments template on the file
system is with [z3c.jbot]. [z3c.jbot] allows you to override any
Plone template just by putting a file in a specific directory.

`z3c.jbot`:: <http://pypi.python.org/pypi/z3c.jbot>

Add z3c.jbot to the dependencies of your package by adding a
line to your setup.py file:

```
install_requires=[
    ...
    'z3c.jbot',
],
```

Register an overrides directory where you can put your file
overrides in your configure.zcml file:

```
<include package="z3c.jbot" file="meta.zcml" />

<browser:jbot
    directory="overrides"
    layer="<layer>" />
```

Replace \<layer> with a custom browserlayer of your package.

Create the template directory we just registered:

```
$ mkdir overrides
```

Copy the comments viewlet template we want to override to the
overrides directory we just created and registered:

```
$ cp ../parts/omelette/plone/app/discussion/browser/comments.pt overrides/plone.app.discussion.browser.comments.pt
```

Restart your Plone instance and you can start to customize
the plone.app.discussion.browser.comments.pt we just created.

## Override the comments viewlet class on the file system

Overriding/subclassing the comments viewlet class is allows you not only to
override the comments viewlet template, but also the comment viewlets view
methods. There are many ways to override components in Plone with the Zope
Component Architecture (ZCA), which is beyond the scope of this howto.

We are going to register our own browserlayer

First we define our browser layer in interfaces.py:

```
from plone.app.discussion.interfaces import IDiscussionLayer

class IMyDiscussionLayer(IDiscussionLayer):
    """Marker interface for a custom plone.app.discussion browser layer
    """
```

Next, we register the browserlayer in our generic setup (GS) setup in the
profiles/default/browserlayer.xml file:

```
<?xml version="1.0"?>
<layers>
  <layer name="my.discussionlayer"
         interface="my.discussion.interfaces.IMyDiscussionLayer" />
</layers>
```

configure.zcml:

```
<!-- Override plone.app.discussion's comments viewlet -->
<browser:viewlet
  name="plone.comments"
  for="Products.CMFCore.interfaces.IContentish"
  layer="my.discussion.interfaces.IDiscussionLayer"
  manager="plone.app.layout.viewlets.interfaces.IBelowContent"
  view="plone.app.layout.globals.interfaces.IViewView"
  class=".comments.CommentsViewlet"
  permission="zope2.View"
  />
```

note: Note that we override the comments viewlet by using the my.discussion.interfaces.IMyDiscussionLayer browser layer and not the default plone.app.discussion.interfaces.IDiscussionLayer browser layer.

Once we registered the custom discussion browser layer and the viewlet, we can create a
comments.py file with our custom version of the comments viewlet:

```
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.discussion.browser.comments import CommentsViewlet as PloneAppDiscussionCommentsViewlet
from plone.app.discussion.browser.comments import CommentForm


class CommentsViewlet(PloneAppDiscussionCommentsViewlet):

    form = CommentForm
    index = ViewPageTemplateFile('comments.pt')

    def get_commenter_home_url(self, username=None):
        if username is None:
            return None
        else:
            return "%s/memberhome/%s" % (self.context.portal_url(), username)
```

To override the comments viewlet template, we create a comment.pt file in the
same directory and copy the contents from the original.
