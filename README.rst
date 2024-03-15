Introduction
============


plone.app.discussion is the commenting system used since Plone 4.1.
It was initially developed as part of the Google Summer of Code 2009 by Timo Stollenwerk (student) and Martin Aspeli (mentor).



Add-on Products
===============

- `collective.autoresizetextarea
  <https://pypi.org/project/collective.autoresizetextarea/>`_
  (for auto-resizing the comment textarea while typing)

- `plone.formwidget.captcha
  <https://pypi.org/project/plone.formwidget.captcha/>`_
  (for Captcha spam protection)

- `plone.formwidget.recaptcha
  <https://pypi.org/project/plone.formwidget.recaptcha/>`_
  (for ReCaptcha spam protection)

- `collective.akismet
  <https://pypi.org/project/collective.akismet/>`_
  (for Akismet spam protection)

- `collective.z3cform.norobots
  <https://pypi.org/project/collective.z3cform.norobots/1.1/>`_
  (provides a "human" captcha widget based on a list of questions/answers)

- `plone.formwidget.hcaptcha
  <https://pypi.org/project/plone.formwidget.hcaptcha/>`_
  (for spam protection by `HCaptcha <https://www.hcaptcha.com/>`_ )

Note: not all of these may be compatible with the current version of ``plone.app.discussion`` and ``Plone`` itself.


Documentation
=============

There is initial `documentation <https://pythonhosted.org/plone.app.discussion/>`_ but it is outdated.
You will still get a feel for how the package is structured though.


Credits
=======

- Timo Stollenwerk
- Martin Aspeli

Many thanks to:

- Jon Stahl (for acting as "the customer" during GSoC)
- David Glick (for technical expertise and advice during GSoC)
- Lennart Regebro (for writing the portal_discussion tool and initial unit tests)
- Carsten Senger (for fixing the comment z3c.form form and pizza)
- Hanno Schlichting (for making p.a.d work with Zope 2.12)
- Alan Hoey (for providing fixes)
- Maik Roeder (for providing and setting up a buildbot)

