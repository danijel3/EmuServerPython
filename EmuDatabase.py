import base64
import glob
import json
import logging
from collections import OrderedDict
from os.path import basename

from twisted.python import log

from Settings import get_setting


class Database:
    def __init__(self, path):
        self.path = path

        files = glob.glob('{}/*_DBconfig.json'.format(path))
        if len(files) == 0:
            raise RuntimeError('Cannot load database!\nConfig file not found in path: {}'.format(path))
        if len(files) > 1:
            log.msg('Warning: more than one config in path! Using only first: {}'.format(files[0]),
                    logLevel=logging.WARN)

        self.config_file = files[0]
        self.ssff_extensions = []

    def get_config(self):
        with open(self.config_file) as f:
            obj = json.load(f)

        for track in obj['ssffTrackDefinitions']:
            self.ssff_extensions.append(track['fileExtension'])

        return obj

    def save_config(self, data):
        with open(self.config_file, 'w') as f:
            json.dump(data, f)

    def get_bundle_list(self):
        bundle_list = []
        sessions = glob.glob(self.path + '/*_ses')
        for sess in sessions:
            sess_name = basename(sess)[:-4]
            bundles = glob.glob(sess + '/*_bndl')
            for bundle in bundles:
                bundle_name = basename(bundle)[:-5]
                bundle_list.append({'name': bundle_name, 'session': sess_name})
        bundle_list = sorted(bundle_list, key=lambda el: el['session'] + '_' + el['name'])
        return bundle_list

    def get_bundle(self, session, bundle):

        bundle_path = '{}/{}_ses/{}_bndl'.format(self.path, session, bundle)

        ret = OrderedDict()
        ssff = []
        ret['ssffFiles'] = ssff

        for ext in self.ssff_extensions:
            ssff_item = OrderedDict()
            ssff.append(ssff_item)
            ssff_item['fileExtension'] = ext
            ssff_item['encoding'] = 'BASE64'
            ssff_item['data'] = self.get_file('{}/{}.{}'.format(bundle_path, bundle, ext))

        wav = OrderedDict()
        ret['mediaFile'] = wav
        wav['encoding'] = 'BASE64'
        wav['data'] = self.get_file('{}/{}.wav'.format(bundle_path, bundle))

        with open('{}/{}_annot.json'.format(bundle_path, bundle)) as f:
            annotation = json.load(f)
        ret['annotation'] = annotation

        return ret

    @staticmethod
    def get_file(path):
        with open(path) as f:
            return base64.b64encode(f.read())

    @staticmethod
    def save_file(path, data):
        with open(path, 'w') as f:
            f.write(base64.b64decode(data))

    def save_bundle(self, session, bundle, data):

        bundle_path = '{}/{}_ses/{}_bndl'.format(self.path, session, bundle)

        for f in data['ssffFiles']:
            fp = '{}/{}.{}'.format(bundle_path, bundle, f['fileExtension'])
            assert f['encoding'] == 'BASE64', 'Only BASE64 encoding supported!'
            self.save_file(fp, f['data'])

        if 'mediaFile' in data and len(data['mediaFile']['data']) > 0:
            fp = '{}/{}.wav'.format(bundle_path, bundle)
            assert data['mediaFile']['encoding'] == 'BASE64', 'Only BASE64 encoding supported!'
            self.save_file(fp, data['mediaFile']['data'])

        annotation = data['annotation']
        with open('{}/{}_annot.json'.format(bundle_path, bundle), 'w') as f:
            json.dump(annotation, f)


def get_database(path):
    if path == '/':
        return Database(get_setting('default_db'))
    elif path in get_setting('db_map'):
        return Database(get_setting('db_map')[path])
    else:
        return None
