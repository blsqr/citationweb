#!/usr/bin/env python3
"""Set up the citationweb"""

from setuptools import setup

INSTALL_DEPS = [
    "scipy>=1.3",
    "numpy>=1.13",
    "PyYAML>=3.12",
    "pypdf2>=1.26",
    "pybtex>=0.21",
    "requests>=2.18",
    "networkx>=2.3",
    "pygraphviz>=1.5",
    "matplotlib>=3.0"
]
TEST_DEPS = [
    "pytest>=3.4.0",
    "pytest-cov>=2.5.1"
]

setup(
    name="citationweb",
    version="1.0-alpha",
    description="Processes BibTex files and creates a network of citations",
    url="https://github.com/blusquare/citationweb",
    author="Yunus Sevinchan",
    author_email="blsqr0@gmail.com",
    license="", # TODO
    packages=["citationweb"],
    package_data=dict(citationweb=["*.yml"]),
    install_requires=INSTALL_DEPS,
    tests_require=TEST_DEPS,
    test_suite="pytest",
    extras_require=dict(test_deps=TEST_DEPS),
    scripts=["cli/cweb"],
    dependency_links=[
        # pdf-extract ruby gem
        "https://github.com/CrossRef/pdfextract"
  ]
)
