#!/usr/bin/python
from distutils.core import setup
import os
import stat

PACKAGE = "futaam"
NAME = "Futaam"
DESCRIPTION = "An anime/manga list manager"
AUTHOR = "HarHar"
AUTHOR_EMAIL = "harhar-captain@live.com"
URL = "https://github.com/HarHar/Futaam"
VERSION = "0.1"

def get_subpackages():
	packs = []
	os.chdir("interfaces")
	for file in os.listdir(os.getcwd()):
		if ".py" in file:
			packs.append("interfaces/" + file[:-3])
	os.chdir("common")
	for file in os.listdir(os.getcwd()):
		if ".py" in file:
			packs.append("interfaces/common/" + file[:-3])
	os.chdir("../..")
	return packs

SUBPACKAGES = get_subpackages()

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
if os.name == "nt":
	print "Why are you using Windows in >2013?"
	print "This script would make things so much more convenient for you if you weren't"
	quit()
else:
	print "Putting a symlink to futaam.py in /usr/bin/"
	try:
		os.symlink("/usr/lib/python2.7/site-packages/futaam.py", "/usr/bin/futaam")
	except:
		os.remove("/usr/bin/futaam")
		os.symlink("/usr/lib/python2.7/site-packages/futaam.py", "/usr/bin/futaam")
	os.popen("chmod +x /usr/bin/futaam")
