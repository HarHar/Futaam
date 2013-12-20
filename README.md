Futaam
======

An anime/manga list manager, originated from YAAM. Aims to be more convenient, less buggy and have more ways of interaction overral.

The name is a [gift](http://archive.foolz.us/a/thread/77916192/) from [/a/](http://boards.4chan.org/a/).

Installing
======
For stable version use

	# pip install futaam

For development version use

	# pip install https://github.com/HarHar/Futaam/zipball/master

Usage
======
For opening a database file

    futaam --INTERFACENAME file.db

For creating a database file
    
    futaam -c

Replace "INTERFACENAME" with the desired interface, or remove the "--INTERFACENAME" entirely and it will default to the text interface

Available interfaces:
  * text
  * gui
  * ncurses
  * web
  * remote
  * irc

Web Interface
=====
The web interface is maintened by [that4chanwolf](https://github.com/that4chanwolf) and is available [here](https://github.com/that4chanwolf/Futaam-Web)

Live examples available [here](http://t4w.me:9001/) and [here](http://futaam.harh.net/)

Remote Interface
====
The remote interface is for accessing your database via internet

Usage (for the server):

    futaam --remote --password CHANGEME --port 1234 [--readonly]

Usage (for the client):

    futaam --INTERFACENAME --host SERVER.IP.OR.HOSTNAME --port 1234
    or
    futaam --INTERFACENAME futa://server.ip.or.hostname:1234

For the client, there will be no change on the 'appearance' of Futaam

Needless to say: replace the password/host, change the port number to your wish and the '--readonly' argument is optional

IRC Interface
====
The IRC interface is a bot that runs as a daemon, and then when using any other interface with the irc hook will make the daemonized bot announce the changes made to the specified channel.

Usage:

    futaam --irc --host irc.server.net --port 6667 --nick MyNick --channel "#anime"
    futaam /path/to/database --INTERFACENAME --hook irc
    
Note that the channel parameter must be enclosed by quotes or have the # escaped

Graphical Interface
====
The GUI for Futaam uses the Qt toolkit to display the entires in the open database and has dialogs for adding, editing, deleting, and swapping entries and viewing additional information (fetched from ANN) about them.

Usage:

	futaam --gui /path/to/database/ [Qt options]

Qt is pretty nifty in that it lets you pass arguements about how you want things to look through the command line. See [this doc](http://pyqt.sourceforge.net/Docs/PyQt4/qapplication.html#QApplication) for more info about this.

See ```/docs/GUI_Interface_Info.md``` for more information.

Hooks
====
Hooks are used for announcing changes made to another place (IRC for instance)
Usage:

    futaam --hook HOOKNAME --INTERFACENAME /path/to/database 
    futaam --hook irc --ncurses /home/john/animu.db

Developers
====
This can be quite confusing for some, but there is a debugging interface (called "debug"), that loads a Futaam file, stores it on a variable called "dbs" and continuously reads raw input and executes it as Python code, that way you can see how the database works and what some functions do. Also you can use the debugging interface as a base for another interface if you'd like.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/HarHar/futaam/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

