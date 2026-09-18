---
myst:
  html_meta:
    "description": "plone.app.discussion documentation"
    "property=og:description": "plone.app.discussion documentation"
    "property=og:title": "plone.app.discussion"
    "keywords": "Plone, Discussion, Comments"
---

# plone.app.discussion

`plone.app.discussion` is the commenting add-on for Plone.

## Introduction

`plone.app.discussion` provides a flexible commenting system for Plone sites. It allows site visitors and members to comment on content objects, with full moderation capabilities and various configuration options.

## Features

- Comment moderation
- Threaded comments
- Email notifications
- Spam protection integration
- Customizable workflows
- Support for anonymous commenting
- Integration with Plone security model

## Installation

If your installation depends on the `Plone` package, you can install it via the Plone control panel.
In case you do only depend on either the `plone.volto`, `plone.classicui` or `Products.CMFPlone` package, you need to add it to your requirements file.
After adding it and installing the requirement, you can install it via the Plone control panel.

## Documentation

```{toctree}
:maxdepth: 2

architecture
design
workflow
captcha
email-notification
auto-approve
components/index
api/index
howtos/index
```

## Indices and tables

* [Index](genindex)
* [Module Index](modindex)
* [Search Page](search)
