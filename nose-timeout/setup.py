# -*- coding: utf-8 -*-

import codecs
import os
import re

from setuptools import setup

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Topic :: Software Development",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.3",
    "Operating System :: OS Independent",
    "Operating System :: POSIX",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS :: MacOS X",
]

NAME = "nose-timeout"


# Standard ``__foo__ = 'bar'`` pairs.
re_meta = re.compile(r"__(\w+?)__\s*=\s*(.*)")
# VERSION tuple
re_vers = re.compile(r"VERSION\s*=\s*\((.*?)\)")
# Module docstring
re_doc = re.compile(r'^"""(.+?)"""')
# We don't need the quotes
rq = lambda s: s.strip("\"'")


def add_default(m):
    """
    Get standard ``__foo__ = 'bar'`` pairs as a (foo, bar) tuple.
    """
    attr_name, attr_value = m.groups()
    return ((attr_name, rq(attr_value)),)


def add_version(m):
    v = list(map(rq, m.groups()[0].split(", ")))
    return (("VERSION", ".".join(v[0:3]) + "".join(v[3:])),)


def add_doc(m):
    """
    Grab the module docstring
    """
    return (("doc", m.groups()[0]),)


pats = {
    re_meta: add_default,
    re_vers: add_version,
    re_doc: add_doc,
}

here = os.path.abspath(os.path.dirname(__file__))
meta_fh = open(os.path.join(here, "nose_timeout/__init__.py"))

# Parse out the package meta information from the __init__ using *shudder*
# regexes
meta = {}
try:
    for line in meta_fh:
        if line.strip() == "# -eof meta-":
            break
        for pattern, handler in pats.items():
            m = pattern.match(line.strip())
            if m:
                meta.update(handler(m))
finally:
    meta_fh.close()

setup(
    name=NAME,
    version=meta["VERSION"],
    description=meta["doc"],
    author=meta["author"],
    author_email=meta["contact"],
    url=meta["homepage"],
    packages=["nose_timeout"],
    license="BSD",
    platforms=["any"],
    classifiers=CLASSIFIERS,
    install_requires=["nose",],
    entry_points={"nose.plugins.0.10": ["timeout = nose_timeout.plugin:NoseTimeout",],},
)
