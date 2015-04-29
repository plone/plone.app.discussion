Introduction
============


plone.app.discussion replaces the old commenting system in Plone 4.1 and is also
available as an add-on product for Plone 3 and 4. It was initially developed as
part of the Google Summer of Code 2009 by Timo Stollenwerk (student) and Martin
Aspeli (mentor).

.. note::

  Make sure you pin down plone.app.discussion to versions < 2.0 if you want to
  install it as an add-on product (see install instructions below for more
  details).

Please report bugs to the `Plone bug tracker`_.

.. _`Plone bug tracker`: http://dev.plone.org/plone/


For the roadmap of the project see our `Pivotal Tracker`_.

.. _`Pivotal Tracker`: http://www.pivotaltracker.com/projects/15135


Requirements
============

Plone 3.3 or later.


Plone 3.3.x Buildout Installation
=================================

To install plone.app.discussion, add the following code to your buildout.cfg::

    [buildout]
    ...
    extends =
        ...
        http://good-py.appspot.com/release/plone.app.discussion/1.0

    ...

    [versions]
    plone.app.discussion = 1.0

    ...

    [instance]
    ...
    eggs =
        ...
        plone.app.discussion

    ...


Plone 4.0 Buildout Installation
===============================

To install plone.app.discussion, add the following code to your buildout.cfg::

    [buildout]

    ...

    versions = versions

    [versions]
    plone.app.discussion = 1.0
    zope.schema = 3.6.4

    ...

    [instance]
    ...
    eggs =
        ...
        plone.app.discussion

    ...


Add-on Products
===============

- `collective.autoresizetextarea
  <http://pypi.python.org/pypi/collective.autoresizetextarea/>`_
  (for auto-resizing the comment textarea while typing)

- `plone.formwidget.captcha
  <http://pypi.python.org/pypi/plone.formwidget.captcha/>`_
  (for Captcha spam protection)

- `plone.formwidget.recaptcha
  <http://pypi.python.org/pypi/plone.formwidget.recaptcha/>`_
  (for ReCaptcha spam protection)

- `collective.akismet
  <http://pypi.python.org/pypi/collective.akismet/>`_
  (for Akismet spam protection)

- `collective.z3cform.norobots
  <http://pypi.python.org/pypi/collective.z3cform.norobots/1.1/>`_
  (provides a "human" captcha widget based on a list of questions/answers)


Documentation
=============

- For developer documentation see
  `http://packages.python.org/plone.app.discussion
  <http://packages.python.org/plone.app.discussion>`_.

- For integrator/end-user documentation see
  `http://plone.org/products/plone.app.discussion/documentation
  <http://plone.org/products/plone.app.discussion/documentation>`_.


Known Issues
============

- **ImportError: No module named owner**: You are trying to install
  plone.app.discussion 2.x on Plone < 4.1. Pin plone.app.discussion to a version
  < 2.0.

- **KeyError: 'Interface `plone.app.discussion.interfaces.IDiscussionSettings`
  defines a field `moderator_email`, for which there is no record.'**: An
  upgrade step was unsuccessful. Reinstall plone.app.discussion to fix this.


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

