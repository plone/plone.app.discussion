from pathlib import Path
from setuptools import find_packages
from setuptools import setup


long_description = (
    f"{Path('README.rst').read_text()}\n{Path('CHANGES.rst').read_text()}"
)


setup(
    name="plone.app.discussion",
    version="5.0.0a1",
    description="Enhanced discussion support for Plone",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.1",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="plone discussion",
    author="Timo Stollenwerk - Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.app.discussion",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "Products.GenericSetup",
        "Products.ZCatalog",
        "Products.statusmessages",
        "plone.api",
        "plone.app.event",
        "plone.registry",
        "plone.resource",
        "plone.autoform",
        "plone.behavior",
        "plone.supermodel",
        "plone.uuid",
        "setuptools",
        "plone.app.layout",
        "plone.app.registry",
        "plone.app.uuid",
        "plone.base",
        "plone.indexer",
        "plone.z3cform",
        "z3c.form>=2.3.3",
        "Zope",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.stringinterp",
            "plone.contentrules",
            "plone.app.contentrules",
            "plone.app.contenttypes[test]",
            "plone.app.robotframework",
            "plone.app.vocabularies",
            "plone.dexterity",
            "plone.testing",
            "plone.protect",
            "Products.MailHost",
            "robotsuite",
            "plone.dexterity",
            "python-dateutil",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
