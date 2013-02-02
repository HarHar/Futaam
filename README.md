Futaam
======

An anime/manga list manager, originated from YAAM. Aims to be more convenient, less buggy and have more ways of interaction overral.

The name is a [gift](http://archive.foolz.us/a/thread/77916192/) from [/a/](http://boards.4chan.org/a/).

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

Web interface
=====
The web interface is maintened by [that4chanwolf](https://github.com/that4chanwolf) and is available [here](https://github.com/that4chanwolf/Futaam-Web)

Remote interface
====
The remote interface is for accessing your database via internet

Usage (for the server):

    futaam --remote --password CHANGEME --port 1234 [--readonly]

Usage (for the client):

    futaam --INTERFACENAME --host SERVER.IP.OR.HOSTNAME --password CHANGEME --port 1234

For the client, there will be no change on the 'appearance' of Futaam

Needless to say: replace the password/host, change the port number to your wish and the '--readonly' argument is optional

IRC interface
====
The IRC interface is a bot that runs as a daemon, and then when using any other interface with the argument '--ircnotify' will make the daemonized bot announce the changes made to the specified channel.

Usage:

    futaam --irc --host irc.server.net --port 6667 --nick MyNick --channel "#anime"
    futaam /path/to/database --INTERFACENAME --ircnotify
    
Note that the channel parameter must be enclosed by quotes or have the # escaped
