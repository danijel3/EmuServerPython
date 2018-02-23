# EmuServerPython

Implementation of an EMU-webApp websocket server in Python.

This project is designed as a starting point for various applications. Currently, two methods of operation are available:

  - serving local files
  - serving files from a Mongo database created by the Clarin speech website project (https://github.com/danijel3/ClarinSpeechWebsite) 

More functionality can be added by creating additional sources (see FileSource for example) and adding them to the sources directory.

## Requirements

Requirements are provided in the `requirements.txt` file and can be installed using:

```
pip install -r requirements.txt 
```

## Usage

Simply run **python ServerMain.py [setings.json]**. It will open a server at the port given in the settings. 

You can connect to it from [EMU-webApp](http://ips-lmu.github.io/EMU-webApp/) (click the connect button) and enter the following address:

    ws://[your-ip-address]:[chosen-port]/[project_id]

Or use the following redirect address to auto-connect:

    http://ips-lmu.github.io/EMU-webApp/?autoConnect=true&serverUrl=ws:%2F%2F[server]:[port]%2F[project_id]

## Settings

A JSON with the following structure:

```
{
    "port": 17890,
    "logFile": "emu_server.log",
    "daemonize": true,
    "pid": "emu_server.pid",
    "source": <your_source_configuration>
}
```

So far, you can use two different source configurations.

  - FileSource:
  
```
"source": {
    "type": "FileSource",
    "db_map": {
      "/test": "/path/to/test",
      "/another/test": "/path/to/another/test"
    },
    "default_db": "/path/to/default/db",
    "authorize": true,
    "user": "user",
    "pass": "pass",
    "readonly": false
  }
```

Note you can set "readonly" to block any modification of the files, or change the individual DB config files to pick 
and choose the ones you want to block. So far, only one universal user/password config is provided and it's cleartext.

  - ClarinDBSource:
  
```
"source": {
    "type": "ClarinDBSource",
    "work_dir": "/path/to/work_dir"
  }
``` 

This source only makes sense if you're running the website, but it can also serve as an inspiration if you're making a 
database-based source of your own.