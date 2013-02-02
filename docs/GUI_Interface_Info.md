GUI Things
======

This document is a list of tips, remarks, links, and other miscellaneous information compiled by the guy who has done most of the work on the Qt interface of Futaam.

For Users
======
* Qt is pretty nifty in that it lets you pass arguements about how you want things to look through the command line.  See (this doc)[http://pyqt.sourceforge.net/Docs/PyQt4/qapplication.html#QApplication] for more info about this.
* I am not a good UI designer.  If you have a suggestion for something that could be improved please or a feature request open an issue or talk to me in #futaam on Rizon.

For Developers
======
* Don't bother trying to edit the .ui files by hand, it always seems to make the parser angry.
* Every string you get back from a PyQt will have the type QString which doesn't make a difference until you are trying to save it to database.  Remeber to use ```str(QString)``` then.
* (PyQt4 Class Reference)[http://pyqt.sourceforge.net/Docs/PyQt4/classes.html] <- It is good to keep this handy.
* The image in the Details dialog is displayed using a HTML ```<img>``` tag because I found the Qt methods for handling drawing an image to be cumbersome and they sometimes caused Python to crash.  If you can do better at me then this please do.
* A real About dialog might be an easy contribution if you're looking for something to do.
* If you have an idea for a Futaam icon and graphical editing skills please contanct me in #futaam on Rizon.
 
