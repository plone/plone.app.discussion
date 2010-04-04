from setuptools import setup, find_packages

version = '1.0b4'

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
      author='Timo Stollenwerk',
      author_email='<plone-developers at lists sourceforge net>',
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
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
