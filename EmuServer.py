import json
from collections import OrderedDict

import bcrypt
from autobahn.twisted.websocket import WebSocketServerProtocol
from twisted.python import log

from EmuDatabase import get_database
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
        log.msg(u"Client connecting: {0}".format(request.peer))
        self.path = request.path
        self.db = get_database(request.path)

    def onMessage(self, payload, is_binary):

        if is_binary:
            self.sendMessage(json.dumps(self.get_error('Received binary data!')))
            return

        request = json.loads(payload)

        self.callbackID = request['callbackID']

        if not self.db:
            self.sendMessage(json.dumps(self.get_error('Cannot find database: ' + self.path)))

        req_type = request['type']

        if req_type == 'GETPROTOCOL':
            self.sendMessage(json.dumps(self.get_reply(self.data_protocol())))
        elif req_type == 'GETDOUSERMANAGEMENT':
            if self.db.password:
                self.sendMessage(json.dumps(self.get_reply('YES')))
            else:
                self.sendMessage(json.dumps(self.get_reply('NO')))
        elif req_type == 'LOGONUSER':
            user = request['userName']
            password = request['pwd']
            # self.sendMessage(json.dumps(self.get_reply('BADUSERNAME')))
            if bcrypt.hashpw(password.encode('utf-8'), self.db.password.encode('utf-8')) != self.db.password.encode(
                    'utf-8'):
                self.sendMessage(json.dumps(self.get_reply('BADPASSWORD')))
            else:
                self.sendMessage(json.dumps(self.get_reply('LOGGEDON')))
        elif req_type == 'GETGLOBALDBCONFIG':
            self.sendMessage(json.dumps(self.get_reply(self.db.get_config())))
        elif req_type == 'GETBUNDLELIST':
            self.sendMessage(json.dumps(self.get_reply(self.db.get_bundle_list())))
        elif req_type == 'GETBUNDLE':
            session = request['session']
            bundle = request['name']
            self.sendMessage(json.dumps(self.get_reply(self.db.get_bundle(session, bundle))))
        elif req_type == 'DISCONNECTWARNING':
            self.sendMessage(json.dumps(self.get_reply(None)))
        elif req_type == 'SAVEBUNDLE':
            if not get_setting('readonly'):
                session = request['data']['session']
                bundle = request['data']['annotation']['name']
                data = request['data']
                self.db.save_bundle(session, bundle, data)
            self.sendMessage(json.dumps(self.get_reply(None)))
        elif req_type == 'SAVECONFIG':
            if not get_setting('readonly'):
                self.db.save_config(request['data'])
            self.sendMessage(json.dumps(self.get_reply(None)))
        else:
            log.msg('NYI ' + req_type)
            self.sendMessage(json.dumps(self.get_error(u'NYI: {}'.format(req_type))))

    def get_error(self, msg):
        res = OrderedDict()
        res['callbackID'] = self.callbackID
        status = OrderedDict()
        res['status'] = status
        status['type'] = 'ERROR'
        status['message'] = msg

        return res

    @staticmethod
    def get_success_status(msg=''):
        status = OrderedDict()
        status['type'] = 'SUCCESS'
        status['message'] = msg
        return status

    def get_reply(self, data, msg=''):
        res = OrderedDict()
        res['callbackID'] = self.callbackID
        if data:
            res['data'] = data
        res['status'] = self.get_success_status(msg)
        return res

    @staticmethod
    def data_protocol():
        data = OrderedDict()
        data['protocol'] = 'EMU-webApp-websocket-protocol'
        data['version'] = '0.0.2'
        return data
