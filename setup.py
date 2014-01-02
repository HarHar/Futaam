#!/usr/bin/python
#from distutils.core import setup
"""The setup script for Futaam"""
from setuptools import setup

PACKAGE = "futaam"
NAME = "Futaam"
DESCRIPTION = "An anime/manga/vn list (backlog) manager"
AUTHOR = "HarHar/TacticalGenius"
AUTHOR_EMAIL = "root@harh.net"
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
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    install_requires=[
        'BeautifulSoup >= 0.1.0',
        'beautifulsoup4 >= 0.1.0',
        'PIL >= 0.1.0',
        'fuzzywuzzy >= 0.1.0',
    ],
    packages=['futaam', 'futaam.tests', 'futaam.interfaces',
	    'futaam.interfaces.common'],
    entry_points={
        'console_scripts': [
            'futaam = futaam.futaam:main',
        ],
        'gui_scripts': [
            'futaam-gui = futaam.futaam:maingui',
        ],
    },
)
