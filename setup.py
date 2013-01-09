#!/usr/bin/python
from distutils.core import setup

PACKAGE = "futaam"
NAME = "Futaam"
DESCRIPTION = "An anime/manga list manager"
AUTHOR = "HarHar"
AUTHOR_EMAIL = "harhar-captain@live.com"
URL = "https://github.com/HarHar/Futaam"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    url=URL,
    py_modules=[PACKAGE],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
