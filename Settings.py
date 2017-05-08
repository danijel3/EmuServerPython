import json

settings = {'port': 17890,
            'default_db': '/path/to/default/db',
            'db_map': {'/one': '/path/to/one/db',
                       '/two': '/path/to/two/db'},
            'authorize': False,
            'user': 'user',
            'pass': 'pass',
            'logFile': None,
            'daemonize': False,
            'pid': 'emu_server.pid',
            'readonly': False}


def get_setting(name):
    if name in settings:
        return settings[name]
    return None


def load_settings(file):
    global settings
    with open(file) as f:
        new_settings = json.load(f)
        for k, v in new_settings.iteritems():
            settings[k] = v


def save_settings(file):
    with open(file, 'w') as f:
        json.dump(settings, f, indent=4)
