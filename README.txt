Introduction
============

plone.app.discussion aims to be the new commenting system for Plone. It was 
initially developed as part of the Google Summer of Code 2009 by Timo 
Stollenwerk (student) and Martin Aspeli (mentor).

For the roadmap of the project see our `Pivotal Tracker`_.

.. _`Pivotal Tracker`: http://www.pivotaltracker.com/projects/15135

Please report bugs to the `Plone bug tracker`_.

.. _`Plone bug tracker`: http://dev.plone.org/plone/


Requirements
============

Plone 3.3 or later.


Plone 3.x Buildout Installation
===============================

To install plone.app.discussion, add the following code to your buildout.cfg::

    [buildout]
    ...
    extends =
        ...
        http://good-py.appspot.com/release/plone.app.discussion/1.0b4

    ...

    [instance]
    ...
    eggs =
        ...
        plone.app.discussion

    ...


Plone 4.x Buildout Installation
===============================

To install plone.app.discussion, add the following code to your buildout.cfg::

    [buildout]
    
    ...
    
    versions = versions
    
    [versions]
    zope.schema = 3.6.0
    
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

