import json
import base64
import glob
from os.path import basename
from collections import OrderedDict
import Settings


class Database:
    def __init__(self, path):
        self.path = path

        files = glob.glob('{}/*_DBconfig.json'.format(path))
        if len(files) == 0:
            raise RuntimeError('Cannot load database!\nConfig file not found in path: {}'.format(path))
        if len(files) > 1:
            print 'Warning: more than one config in path! Using only first: {}'.format(files[0])

        self.config_file = files[0]
        self.ssff_extensions = []

    def getConfig(self):
        with open(self.config_file) as f:
            obj = json.load(f)

        for track in obj['ssffTrackDefinitions']:
            self.ssff_extensions.append(track['fileExtension'])

        return obj

    def getBundleList(self):
        list = []
        sessions = glob.glob(self.path + '/*_ses')
        for sess in sessions:
            sessname = basename(sess)[:-4]
            bundles = glob.glob(sess + '/*_bndl')
            for bndl in bundles:
                bndlname = basename(bndl)[:-5]
                list.append({'name': bndlname, 'session': sessname})
        list=sorted(list,key=lambda el: el['session']+'_'+el['name'])
        return list

    def getBundle(self, session, bundle):

        bdnl_path = '{}/{}_ses/{}_bndl'.format(self.path, session, bundle)

        ret = OrderedDict()
        ssff = []
        ret['ssffFiles'] = ssff

        for ext in self.ssff_extensions:
            ssff_item = OrderedDict()
            ssff.append(ssff_item)
            ssff_item['fileExtension'] = ext
            ssff_item['encoding'] = 'BASE64'
            ssff_item['data'] = self.getFile('{}/{}.{}'.format(bdnl_path, bundle, ext))

        wav = OrderedDict()
        ret['mediaFile'] = wav
        wav['encoding'] = 'BASE64'
        wav['data'] = self.getFile('{}/{}.wav'.format(bdnl_path, bundle))

        with open('{}/{}_annot.json'.format(bdnl_path, bundle)) as f:
            annot = json.load(f)
        ret['annotation'] = annot

        return ret

    def getFile(self, path):
        with open(path) as f:
            return base64.b64encode(f.read())


def getDatabase(path):
    if path == '/':
        return Database(Settings.settings['default_db'])
    elif path in Settings.settings['db_map']:
        return Database(Settings.settings['db_map'][path])
    else:
        return None
