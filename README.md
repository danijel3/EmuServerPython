# EmuServerPython

Implementation of an EMU-webApp websocket server in Python. This branch is used specifically for the Clarin Website. 

# Requirements

Installable using *pip* or *easy_install*:

  * autobahn - for websockets
  * monogodb
  * pymongo
  
# usage

Simply run **python ServerMain.py [setings.json]**. It will open a server at the given port. You can connect to it from 
[EMU-webApp](http://ips-lmu.github.io/EMU-webApp/) (click the connect button) and enter the following address:

    ws://[your-ip-address]:[chosen-port]/[project_id]

Or use the following redirect address to auto-connect:

    http://ips-lmu.github.io/EMU-webApp/?autoConnect=true&serverUrl=ws:%2F%2F[server]:[port]%2F[project_id]

## Settings

A JSON with the following structure:

    {
            'port': 17890,
            'logFile': None,
            'daemonize': False,
            'pid': 'emu_server.pid',
            'work_dir': 'path/to/workdir'
    }
