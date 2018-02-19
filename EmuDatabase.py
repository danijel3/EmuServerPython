import base64
import codecs
import datetime
import hashlib
import os
from collections import OrderedDict

from bson import ObjectId
from pymongo import MongoClient

from Config import get_config
from Segmentation import segmentation_to_emu_annot, annot_to_ctm
from Settings import get_setting

db = MongoClient()


def get_file_path(work_dir, id):
    file = db.clarin.resources.find_one({'_id': ObjectId(id)})
    return os.path.join(work_dir, file['file'])


def get_file(work_dir, id):
    with open(get_file_path(work_dir, id)) as f:
        return base64.b64encode(f.read())


def file_hash(filename):
    h = hashlib.sha1()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda: f.read(128 * 1024), b''):
            h.update(b)
    return h.hexdigest()


# TODO make new version instead of modifying in-place?
def save_file(work_dir, id, data):
    path = get_file_path(work_dir, id)
    with codecs.open(path, mode='w', encoding='utf-8') as f:
        f.write(data)
    hash = file_hash(path)
    db.clarin.resources.update_one({'_id': ObjectId(id)}, {
        '$set': {'hash': hash, 'modified': datetime.datetime.utcnow(), 'from.task': 'emu-sdms',
                 'from_hash': 'invalid'}})


class Database:
    def __init__(self, proj_id):
        self.proj = db.clarin.emu.find_one({'_id': ObjectId(proj_id)})
        if not self.proj:
            raise RuntimeError
        self.work_dir = get_setting('work_dir')
        self.password = None
        if self.proj['visibility'] == 'private':
            self.password = self.proj['password']

    def get_config(self):
        return get_config('emu_database')

    def save_config(self, data):
        pass

    def get_bundle_list(self):
        bundle_list = []
        for name, bundle in self.proj['bundles'].iteritems():
            if 'seg' in bundle and 'audio' in bundle:
                bundle_list.append({'name': name, 'session': bundle['session']})
        bundle_list = sorted(bundle_list, key=lambda el: el['session'] + '_' + el['name'])
        return bundle_list

    def get_bundle(self, session, bundle):

        bndl = self.proj['bundles'][bundle]

        ret = OrderedDict()
        ret['ssffFiles'] = []

        wav = OrderedDict()
        ret['mediaFile'] = wav
        wav['encoding'] = 'BASE64'
        wav['data'] = get_file(self.work_dir, bndl['audio'])

        annotation = segmentation_to_emu_annot(get_file_path(self.work_dir, bndl['seg']), bundle)
        ret['annotation'] = annotation

        return ret

    def save_bundle(self, session, bundle, data):
        bndl = self.proj['bundles'][bundle]
        id = bndl['seg']
        save_file(self.work_dir, id, annot_to_ctm(data['annotation']))


def get_database(path):
    try:
        return Database(path[1:])
    except RuntimeError:
        return None
