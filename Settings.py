import json

settings = {'port': 17890,
            'logFile': None,
            'daemonize': False,
            'pid': 'emu_server.pid',
            'work_dir': 'path/to/workdir'}


def get_setting(name):
    if name in settings:
        return settings[name]
    return None


def load_settings(file):
    global settings
    with open(file) as f:
        new_settings = json.load(f)
        for k, v in new_settings.items():
            settings[k] = v


def save_settings(file):
    with open(file, 'w') as f:
        json.dump(settings, f, indent=4)
