# EmuServerPython

Implementation of an EMU-webApp websocket server in Python. It may be convinient if someone wants to share data to EMU-webApp,
but doesn't want to install/use node.js (Python is is available almost everywhere).

# Requirements

Installable using *pip* or *easy_install*:

  * autobahn - for websockets
  
# usage

Simply run **python ServerMain.py [setings.json]**. It will open a server at the given port. You can connect to it from 
[EMU-webApp](http://ips-lmu.github.io/EMU-webApp/) (click the connect button) and enter the following address:

    ws://[your-ip-address]:[chosen-port]/[optional-websocket-path]

By changing the websocket path you can share multiple databases.

## Settings

A JSON with the following structure:

    {
        "db_map": {
            "/websocket-path": "/path/to/db",
            "/another-websocket-path": "/path/to/another/db",             
        }, 
        "port": 17890, 
        "default_db": "/path/to/default/db"
    }
