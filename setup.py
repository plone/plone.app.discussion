from setuptools import find_packages
from setuptools import setup

version = '2.4.0.dev0'

install_requires = [
    'setuptools',
    'collective.monkeypatcher',
    'plone.app.layout',
    'plone.app.registry',
    'plone.app.uuid',
    'plone.app.z3cform',
    'plone.indexer',
    'plone.registry',
    'plone.z3cform',
    'Products.CMFPlone',
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
      description="Enhanced discussion support for Plone",
      long_description=open("README.rst").read() + "\n" +
      open("CHANGES.rst").read(),
      classifiers=[
          "Development Status :: 1 - Planning",
          "Framework :: Plone",
          "Framework :: Plone :: 3.3",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Programming Language :: Python",
      ],
      keywords='plone discussion',
      author='Timo Stollenwerk - Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.discussion',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
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
              'plone.app.robotframework[ride,reload]',
          ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

