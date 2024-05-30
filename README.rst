Introduction
============

plone.app.discussion is the commenting add-on for Plone.
It is part of the maintained Plone core.

Installation
============

If your installation depends on the `Plone <https://pypi.org/project/Plone/>`_ package, you can install it via the Plone control panel.
In case you do only depend on either the `plone.volto`, `plone.classicui` or `Products.CMFPlone` package, you need to add it to your requirements file.
After adding it and installing the requirement, you can install it via the Plone control panel.


Spam protection
===============

These days it is essential to protect your site from commenting spam.
The following add-ons can help to protect your site:

- `plone.formwidget.captcha
  <https://pypi.org/project/plone.formwidget.captcha/>`_
  (for Captcha spam protection)

- `plone.formwidget.recaptcha
  <https://pypi.org/project/plone.formwidget.recaptcha/>`_
  (for ReCaptcha spam protection)

- `collective.z3cform.norobots
  <https://pypi.org/project/collective.z3cform.norobots/>`_
  (provides a "human" captcha widget based on a list of questions/answers)

- `plone.formwidget.hcaptcha
  <https://pypi.org/project/plone.formwidget.hcaptcha/>`_
  (for spam protection by `HCaptcha <https://www.hcaptcha.com/>`_ )


Documentation
=============

For further information, please refer to the `official Plone documentation <https://docs.plone.org/>`_.

Credits
=======

This package was initially developed as part of the Google Summer of Code 2009 by Timo Stollenwerk (student) and Martin Aspeli (mentor).

Many thanks to:

- Jon Stahl (for acting as "the customer" during GSoC)
- David Glick (for technical expertise and advice during GSoC)
- Lennart Regebro (for writing the portal_discussion tool and initial unit tests)
- Carsten Senger (for fixing the comment z3c.form form and pizza)
- Hanno Schlichting (for making p.a.d work with Zope 2.12)
- Alan Hoey (for providing fixes)
- Maik Roeder (for providing and setting up a buildbot)
- Jens Klein (for ripping it out of core and making it a separate core-addon for Plone 6.1)
