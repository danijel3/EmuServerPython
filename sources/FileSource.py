import json
import logging
from collections import OrderedDict
from pathlib import Path

from twisted.python import log

from EmuSource import EmuSource
from Settings import get_setting


class FileSource(EmuSource):
    def __init__(self, url_path):

        if not url_path or url_path == '/':
            file_path = get_setting('source', 'default_db')
        elif url_path in get_setting('source', 'db_map'):
            file_path = get_setting('source', 'db_map', url_path)
        else:
            raise RuntimeError(f'Cannot load database!\nMissing path in configuration: {url_path}')

        self.path = Path(file_path)

        files = list(self.path.glob('*_DBconfig.json'))
        if len(files) == 0:
            raise RuntimeError(f'Cannot load database!\nConfig file not found in path: {url_path}')
        if len(files) > 1:
            log.msg(f'Warning: more than one config in path! Using only first: {files[0]}', logLevel=logging.WARN)

        self.config_file = files[0]
        self.ssff_extensions = []

    def do_login(self):
        return get_setting('source', 'authorize')

    def check_user(self, user):
        return True

    def check_login(self, user, passwd):
        return user == get_setting('source', 'user') and passwd == get_setting('source', 'pass')

    def get_config(self):
        with open(self.config_file) as f:
            obj = json.load(f)

        for track in obj['ssffTrackDefinitions']:
            self.ssff_extensions.append(track['fileExtension'])

        return obj

    def save_config(self, data):
        if get_setting('source', 'readonly'):
            return
        with open(self.config_file, 'w') as f:
            json.dump(data, f)

    def get_bundle_list(self):
        bundle_list = []
        sessions = self.path.glob('*_ses')
        for sess in sessions:
            sess_name = sess.name[:-4]
            bundles = sess.glob('*_bndl')
            for bundle in bundles:
                bundle_name = bundle.name[:-5]
                bundle_list.append({'name': bundle_name, 'session': sess_name})
        bundle_list = sorted(bundle_list, key=lambda el: el['session'] + '_' + el['name'])
        return bundle_list

    def get_bundle(self, session, bundle):
        bundle_path = self.path / f'{session}_ses' / f'{bundle}_bndl'

        ret = OrderedDict()
        ssff = []
        ret['ssffFiles'] = ssff

        for ext in self.ssff_extensions:
            ssff_item = OrderedDict()
            ssff.append(ssff_item)
            ssff_item['fileExtension'] = ext
            ssff_item['encoding'] = 'BASE64'
            ssff_item['data'] = self.get_file(bundle_path / f'{bundle}.{ext}', base64_enc=True)

        wav = OrderedDict()
        ret['mediaFile'] = wav
        wav['encoding'] = 'BASE64'
        wav['data'] = self.get_file(bundle_path / f'{bundle}.wav', base64_enc=True)

        with open(bundle_path / f'{bundle}_annot.json') as f:
            annotation = json.load(f)
        ret['annotation'] = annotation

        return ret

    def save_bundle(self, session, bundle, data):
        if get_setting('source', 'readonly'):
            return

        bundle_path = self.path / f'{session}_ses' / f'{bundle}_bndl'

        for f in data['ssffFiles']:
            ext = f['fileExtension']
            fp = bundle_path / f'{bundle}.{ext}'
            assert f['encoding'] == 'BASE64', 'Only BASE64 encoding supported!'
            self.save_file(fp, f['data'], base64_dec=True)

        if 'mediaFile' in data and len(data['mediaFile']['data']) > 0:
            fp = bundle_path / f'{bundle}.wav'
            assert data['mediaFile']['encoding'] == 'BASE64', 'Only BASE64 encoding supported!'
            self.save_file(fp, data['mediaFile']['data'], base64_dec=True)

        annotation = data['annotation']
        with open(bundle_path / f'{bundle}_annot.json', 'w') as f:
            json.dump(annotation, f)
