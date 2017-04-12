import json

settings = {'port': 17890,
            'default_db': '/home/guest/PycharmProjects/CTMtoEMU/test',
            'db_map': {'/test': '/home/guest/PycharmProjects/CTMtoEMU/test',
                       '/ae':
                           '/home/guest/PycharmProjects/CTMtoEMU/emuR_demoData/ae_emuDB'}}


def load_settings(file):
    global settings
    with open(file) as f:
        settings = json.load(f)

def save_settings(file):
    with open(file, 'w') as f:
        json.dump(settings, f, indent=4)
