# EmuServerPython

Implementation of an EMU-webApp websocket server in Python. It may be convinient if someone wants to share data to EMU-webApp,
but doesn't want to install/use node.js (Python is is available almost everywhere).

# Requirements

Installable using *pip* or *easy_install*:

  * autobahn - for websockets
  
# usage

Simply run **python ServerMain.py [setings.json]**. It will open a server at the given port. You can connect to it from 
[EMU-webApp](http://ips-lmu.github.io/EMU-webApp/) (click the connect button) and enter the following address:

    ws://[your-ip-address]:[chosen-port]/[mongo_project_id]/[tool_name]

This branch is specifically for the Clarin-PL speech tools website. The path refers to the IDs in the MongoDB of the 
website. The server automatically looks for the path and verifies the password if it exists.

## Settings

A JSON with the following structure:

    {
        "port": 17890, 
        "logFile": None,
        "daemonize": False,
        "pid": "emu_server.pid"
    }
