from setuptools import setup, find_packages
import os

version = '1.0b2'

setup(name='plone.app.discussion',
      version=version,
      description="Enhanced discussion support for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Timo Stollenwerk',
      author_email='timo@zmag.de',
      url='http://pypi.python.org/pypi/plone.app.discussion',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.autopermission',
          'collective.monkeypatcher',
          'plone.app.registry',
          'plone.app.z3cform',
          'plone.indexer',
          'plone.registry',
          'plone.z3cform<=0.5.7',
          'ZODB3',
          'zope.interface',
          'zope.component',
          'zope.annotation',
          'zope.event',
          'zope.container',
          'zope.lifecycleevent',
          'zope.site',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
