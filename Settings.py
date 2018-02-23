import json

settings = {'port': 17890,
            'logFile': None,
            'daemonize': False,
            'pid': 'emu_server.pid',
            'secure': False,
            'tls': {'private': 'server.key', 'cert': 'server.crt'},
            'source': None}


def get_setting(name, *argv):
    if name not in settings:
        return None
    ret = settings[name]
    for arg in argv:
        if arg not in ret:
            return None
        ret = ret[arg]
    return ret


def load_settings(file):
    global settings
    with open(file) as f:
        new_settings = json.load(f)
        for k, v in new_settings.items():
            settings[k] = v


def save_settings(file):
    with open(file, 'w') as f:
        json.dump(settings, f, indent=4)
