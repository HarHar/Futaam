#!/usr/bin/python
from distutils.core import setup
import os

PACKAGE = "futaam"
SUBPACKAGES = ["interfaces", "parser"]
NAME = "Futaam"
DESCRIPTION = "An anime/manga list manager"
AUTHOR = "HarHar"
AUTHOR_EMAIL = "harhar-captain@live.com"
URL = "https://github.com/HarHar/Futaam"
VERSION = "0.1"

def get_interfaces():
	ifs = []
	os.chdir("interfaces")
	for file in os.listdir(os.getcwd()):
		if ".py" in file:
			ifs.append("interfaces/" + file[:-3])
	os.chdir("..")
	return ifs
INTERFACES = get_interfaces()
SUBPACKAGES = ["parser"] + INTERFACES

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    url=URL,
    py_modules=[PACKAGE] + SUBPACKAGES,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
