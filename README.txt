Introduction
============

plone.app.discussion aims to be the new commenting system for Plone 4.1. It was developed as part of the Google Summer of Code 2009 by Timo Stollenwerk (student) and Martin Aspeli (mentor).

For details on the progress of this project, visit our `Pivotal Tracker`_.

.. _`Pivotal Tracker`: http://www.pivotaltracker.com/projects/15135

Feel free to send bug reports to timo@zmag.de.

Disclaimer
==========

This is an alpha release! Alpha releases should only be used for testing and development.

Requirements
============

Plone 3.3 or later.

Buildout Installation
=====================

To install plone.app.discussion, add the following code to your buildout.cfg::

    [buildout]
    ...
    extends =
        ...
        http://good-py.appspot.com/release/plone.app.discussion/1.0a1

    ...

    [instance]
    ...
    eggs =
        ...
        plone.app.discussion

    ...


Credits
=======

- Timo Stollenwerk
- Martin Aspeli
- Jon Stahl
- David Glick
- Lennart Regebro
- Carsten Senger
- Hanno Schlichting
