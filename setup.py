import sys
from setuptools import setup, find_packages

version = '1.1.1'

install_requires = [
    'setuptools',
    'collective.autopermission',
    'collective.monkeypatcher',
    'plone.app.layout',
    'plone.app.registry',
    'plone.app.z3cform',
    'plone.indexer',
    'plone.registry',
    'plone.z3cform',
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

# On Python 2.6 (implying Plone 4), require plone.app.uuid
if sys.version_info >= (2,6):
    install_requires.append('plone.app.uuid')

setup(name='plone.app.discussion',
      version=version,
      description="Enhanced discussion support for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
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
      extras_require = {
          'test': [
              'plone.app.testing',
              'interlude',
          ]
      },      
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
