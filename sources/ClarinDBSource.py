import datetime
import hashlib
import json
from collections import OrderedDict
from os import close
from pathlib import Path
from tempfile import mkstemp

import bcrypt
from bson import ObjectId
from pymongo import MongoClient

from EmuSource import EmuSource
from Settings import get_setting
from sources.ClarinDBConfig import get_config
from sources.ClarinDBSegmentation import segmentation_to_emu_annot, annot_to_ctm

db = MongoClient()


def file_hash(filename):
    h = hashlib.sha1()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda: f.read(128 * 1024), b''):
            h.update(b)
    return h.hexdigest()


class ClarinDBSource(EmuSource):
    def __init__(self, proj_id):
        self.proj = db.clarin.emu.find_one({'_id': ObjectId(proj_id[1:])})
        if not self.proj:
            raise RuntimeError
        self.work_dir = Path(get_setting('source', 'work_dir'))
        self.password = None
        if self.proj['visibility'] == 'private':
            self.password = self.proj['password']

    def do_login(self):
        return self.password is not None

    def check_user(self, user):
        return True

    def check_login(self, user, passwd):
        return bcrypt.hashpw(passwd.encode('utf-8'), self.password) == self.password

    def get_config(self):
        return get_config('emu_database')

    def save_config(self, data):
        pass

    def get_bundle_list(self):
        bundle_list = []
        for name, bundle in self.proj['bundles'].items():
            if 'seg' in bundle and 'audio' in bundle:
                bundle_list.append({'name': name, 'session': bundle['session']})
        bundle_list = sorted(bundle_list, key=lambda el: el['session'] + '_' + el['name'])
        return bundle_list

    def get_file_path(self, fid):
        file = db.clarin.resources.find_one({'_id': ObjectId(fid)})
        return self.work_dir / file['file']

    def get_bundle(self, session, bundle):
        bndl = self.proj['bundles'][bundle]

        ret = OrderedDict()
        ret['ssffFiles'] = []

        wav = OrderedDict()
        ret['mediaFile'] = wav
        wav['encoding'] = 'BASE64'
        wav['data'] = self.get_file(self.get_file_path(bndl['audio']), base64_enc=True)

        annotation = segmentation_to_emu_annot(self.get_file_path(bndl['seg']), bundle)
        ret['annotation'] = annotation

        return ret

    def save_bundle(self, session, bundle, data):
        bndl = self.proj['bundles'][bundle]

        work_dir = get_setting('source', 'work_dir')

        fd, new_path = mkstemp(dir=work_dir)
        close(fd)
        new_path = Path(work_dir) / new_path
        self.save_file(new_path, annot_to_ctm(data['annotation']))

        hash = file_hash(new_path)

        file = db.clarin.resources.find_one({'hash': hash})
        if file:
            id = file['_id']
            new_path.unlink()
        else:
            time = datetime.datetime.utcnow()
            from_task = {'task': 'emu-smds', 'seg': bndl['seg']}
            from_hash = hashlib.sha1(json.dumps(from_task).encode('utf-8')).hexdigest()

            res = db.clarin.resources.insert_one(
                {'file': new_path.name, 'type': 'segmentation', 'hash': hash, 'created': time, 'modified': time,
                 'from': from_task, 'from_hash': from_hash})
            id = res.inserted_id

        db.clarin.emu.update_one({'_id': ObjectId(self.proj['_id'])}, {'$set': {f'bundles.{bundle}.seg': id}})
