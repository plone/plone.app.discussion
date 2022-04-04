# encoding: utf-8

from setuptools import find_packages
from setuptools import setup


version = '4.0.0a5'

install_requires = [
    'setuptools',
    'plone.app.layout',
    'plone.app.registry',
    'plone.app.uuid',
    'plone.app.z3cform',
    'plone.indexer',
    'plone.registry',
    'plone.z3cform',
    'six',
    'ZODB3',
    'zope.interface',
    'zope.component',
    'zope.annotation',
    'zope.event',
    'zope.container',
    'zope.lifecycleevent',
    'zope.site',
    'z3c.form>=2.3.3',
]

setup(name='plone.app.discussion',
      version=version,
      description='Enhanced discussion support for Plone',
      long_description=open('README.rst').read() + '\n' +
      open('CHANGES.rst').read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 6.0",
          "Framework :: Plone :: Core",
          "Framework :: Zope :: 5",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
      ],
      keywords='plone discussion',
      author='Timo Stollenwerk - Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://pypi.org/project/plone.app.discussion',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require={
          'test': [
              'plone.app.testing',
              'plone.stringinterp',
              'plone.contentrules',
              'plone.app.contentrules',
              'plone.app.contenttypes[test]',
              'plone.app.robotframework',
          ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
