#!/usr/bin/python
try:
    import pip
except ImportError, e:
    import urllib2
    exec urllib2.urlopen("http://python-distribute.org/distribute_setup.py").read()
    exec urllib2.urlopen("https://raw.github.com/pypa/pip/master/contrib/get-pip.py").read()

try:
    import PIL, beautifulsoup4, BeautifulSoup
except ImportError, e:
    from pip.index import PackageFinder
    from pip.req import InstallRequirement, RequirementSet
    from pip.locations import build_prefix, src_prefix
     
    requirement_set = RequirementSet(
        build_dir=build_prefix,
        src_dir=src_prefix,
        download_dir=None)
     
    requirement_set.add_requirement(InstallRequirement.from_line("BeautifulSoup", None))
    requirement_set.add_requirement(InstallRequirement.from_line("beautifulsoup4", None))
    requirement_set.add_requirement(InstallRequirement.from_line("PIL", None))



    install_options = []
    global_options = []
    finder = PackageFinder(find_links=[], index_urls=["http://pypi.python.org/simple/"])
     
    requirement_set.prepare_files(finder, force_root_egg_info=False, bundle=False)
    requirement_set.install(install_options, global_options)

from distutils.core import setup
import os
import sys
import stat
import platform

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

def get_ui_files():
	files = []
	os.chdir("interfaces/ui/")
	for fileName in os.listdir(os.getcwd()):
		if fileName[-2:] == "ui":
			files.append("interfaces/ui/"+fileName)
	os.chdir("../../")
	return files

UI_FILES = get_ui_files() 

python_version_string = str(platform.python_version[0]) + "." + str(platform.python_version[1])

if os.name == "nt":
	data_file_location = sys.prefix + "\\Scripts\\futaam"
else:
	if python_version[0] >= 2 and python_version[1] >= 6:
    	data_file_location = sys.prefix + "/local/share/futaam"
	else:
		data_file_location = sys.prefix + "/share/futaam"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    url=URL,
    py_modules=[PACKAGE] + SUBPACKAGES,
    data_files=[(data_file_location, UI_FILES)],
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
	path = sys.prefix + "\\Lib\\site-packages\\futaam.py"
	os.popen("set PATH=%PATH%;" + path)
else:
	print "Putting a symlink to futaam.py in /usr/bin/"
	try:
		os.symlink("/usr/lib/python"+ python_version_string +"/site-packages/futaam.py", "/usr/bin/futaam")
	except:
		os.remove("/usr/bin/futaam")
		os.symlink("/usr/lib/python"+ python_version_string +"/site-packages/futaam.py", "/usr/bin/futaam")
		os.popen("chmod +x /usr/bin/futaam")
