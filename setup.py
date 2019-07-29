#!/usr/bin/env python

from setuptools import find_packages, setup

from django_flexquery import __version__


setup(
    name="django-flexquery",
    version=__version__,
    description="Reusable QuerySet filtering logic for Django, incorporating the DRY principle and maximizing user experience and performance",
    long_description=open("README.rst").read(),
    author="Robert Schindler",
    author_email="r.schindler@efficiosoft.com",
    url="https://github.com/efficiosoft/django-flexquery",
    license="MIT License",
    packages=find_packages("."),
    install_requires=("django ~= 2.0",),
)
