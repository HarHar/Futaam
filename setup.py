#!/usr/bin/python
from distutils.core import setup
import os
import stat
import platform

def cutDot(t, d):
	out = ''
	dc = 0
	for l in t:
		out += l
		if l == '.':
			dc += 1
		if dc == d:
			break
	return out

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
		if file[-2:] == "py":
			packs.append("interfaces/" + file[:-3])
	os.chdir("common")
	for file in os.listdir(os.getcwd()):
		if file[-2:] == "py":
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
	print "Adding Futaam to your path"
	path = "C:\\Python" + cutDot(platform.python_version(), 2).rstrip('.') + "\\Lib\\site-packages\\futaam.py"
	os.popen("set PATH=%PATH%;" + path)
else:
	print "Putting a symlink to futaam.py in /usr/bin/"
	try:
		os.symlink("/usr/lib/python"+ cutDot(platform.python_version(), 2).rstrip('.') +"/site-packages/futaam.py", "/usr/bin/futaam")
	except:
		os.remove("/usr/bin/futaam")
		os.symlink("/usr/lib/python"+ cutDot(platform.python_version(), 2).rstrip('.') +"/site-packages/futaam.py", "/usr/bin/futaam")
		os.popen("chmod +x /usr/bin/futaam")
