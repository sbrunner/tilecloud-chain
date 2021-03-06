# -*- coding: utf-8 -*-

import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as r:
    with open(os.path.join(here, "CHANGES.md")) as c:
        README = r.read() + "\n\n" + c.read()

install_requires = [
    "c2cwsgiutils",
    "Jinja2",
    "pykwalify",
    "pyramid_mako",
    "PyYAML",
    "Shapely",
    "tilecloud>=1.3.0",
]

setup(
    name="tilecloud-chain",
    version="1.16.0",
    description=(
        "Tools to generate tiles from WMS or Mapnik, to S3, "
        "Berkeley DB, MBTiles, or local filesystem in WMTS layout using "
        "Amazon cloud services."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    author="Stéphane Brunner",
    author_email="stephane.brunner@camptocamp.com",
    url="http://github.com/camptocamp/tilecloud-chain",
    license="BSD",
    keywords="gis tilecloud chain",
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "generate_tiles = tilecloud_chain.generate:main",
            "generate_controller = tilecloud_chain.controller:main",
            "generate_cost = tilecloud_chain.cost:main",
            "generate_copy = tilecloud_chain.copy_:main",
            "generate_process = tilecloud_chain.copy_:process",
            "import_expiretiles = tilecloud_chain.expiretiles:main",
        ],
        "pyramid.scaffold": ["tilecloud_chain = tilecloud_chain.scaffolds:Create"],
        "paste.app_factory": ["main = tilecloud_chain.server:main"],
    },
)
