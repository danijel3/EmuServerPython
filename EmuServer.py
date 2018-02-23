import json
from collections import OrderedDict

from autobahn.twisted.websocket import WebSocketServerProtocol
from twisted.python import log

from EmuSource import get_source
from Settings import get_setting


# dummy Future implementation
class Future:
    def __init__(self):
        pass

    def callback(self, result):
        pass


class EmuServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        self.path = None
        self.callbackID = None
        self.db = None
        self.is_closed = Future()

    def onConnect(self, request):
        log.msg("Client connecting: {0}".format(request.peer))
        self.path = request.path
        self.db = get_source(request.path)

    def onMessage(self, payload, is_binary):

        if is_binary:
            self.sendMessage(self.get_error('Received binary data!'))
            return

        request = json.loads(payload)

        self.callbackID = request['callbackID']

        if not self.db:
            self.sendMessage(self.get_error('Cannot find database: ' + self.path))

        req_type = request['type']

        if req_type == 'GETPROTOCOL':
            self.sendMessage(self.get_reply(self.data_protocol()))
        elif req_type == 'GETDOUSERMANAGEMENT':
            if self.db.do_login():
                self.sendMessage(self.get_reply('YES'))
            else:
                self.sendMessage(self.get_reply('NO'))
        elif req_type == 'LOGONUSER':
            user = request['userName']
            password = request['pwd']
            if not self.db.check_user(user):
                self.sendMessage(self.get_reply('BADUSERNAME'))
            elif not self.db.check_login(user, password):
                self.sendMessage(self.get_reply('BADPASSWORD'))
            else:
                self.sendMessage(self.get_reply('LOGGEDON'))
        elif req_type == 'GETGLOBALDBCONFIG':
            self.sendMessage(self.get_reply(self.db.get_config()))
        elif req_type == 'GETBUNDLELIST':
            self.sendMessage(self.get_reply(self.db.get_bundle_list()))
        elif req_type == 'GETBUNDLE':
            session = request['session']
            bundle = request['name']
            self.sendMessage(self.get_reply(self.db.get_bundle(session, bundle)))
        elif req_type == 'DISCONNECTWARNING':
            self.sendMessage(self.get_reply(None))
        elif req_type == 'SAVEBUNDLE':
            if not get_setting('readonly'):
                session = request['data']['session']
                bundle = request['data']['annotation']['name']
                data = request['data']
                self.db.save_bundle(session, bundle, data)
            self.sendMessage(self.get_reply(None))
        elif req_type == 'SAVECONFIG':
            if not get_setting('readonly'):
                self.db.save_config(request['data'])
            self.sendMessage(self.get_reply(None))
        else:
            log.msg('NYI ' + req_type)
            self.sendMessage(self.get_error('NYI: {}'.format(req_type)))

    def get_error(self, msg):
        res = OrderedDict()
        res['callbackID'] = self.callbackID
        res['status'] = OrderedDict()
        res['status']['type'] = 'ERROR'
        res['status']['message'] = msg

        return json.dumps(res).encode('utf-8')

    def get_reply(self, data, msg=''):
        res = OrderedDict()
        res['callbackID'] = self.callbackID
        if data:
            res['data'] = data

        res['status'] = OrderedDict()
        res['status']['type'] = 'SUCCESS'
        res['status']['message'] = msg

        return json.dumps(res).encode('utf-8')

    @staticmethod
    def data_protocol():
        data = OrderedDict()
        data['protocol'] = 'EMU-webApp-websocket-protocol'
        data['version'] = '0.0.2'
        return data
