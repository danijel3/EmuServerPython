from autobahn.twisted.websocket import WebSocketServerProtocol
from collections import OrderedDict
import json

from EmuDatabase import getDatabase


# dummy Future implementation
class Future:
    def callback(self, result):
        pass


class EmuServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        self.callbackID = None
        self.db = None
        self.is_closed = Future()

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.path = request.path
        self.db = getDatabase(request.path)

    def onMessage(self, payload, isBinary):

        if isBinary:
            self.sendMessage(json.dumps(self.getError('Received binary data!')))
            return

        request = json.loads(payload)

        self.callbackID = request['callbackID']

        if not self.db:
            self.sendMessage(json.dumps(self.getError('Cannot find database: ' + self.path)))

        type = request['type']

        if type == 'GETPROTOCOL':
            self.sendMessage(json.dumps(self.getReply(self.dataProtocol())))
        elif type == 'GETDOUSERMANAGEMENT':
            self.sendMessage(json.dumps(self.getReply('NO')))
        elif type == 'GETGLOBALDBCONFIG':
            self.sendMessage(json.dumps(self.getReply(self.db.getConfig())))
        elif type == 'GETBUNDLELIST':
            self.sendMessage(json.dumps(self.getReply(self.db.getBundleList())))
        elif type == 'GETBUNDLE':
            session = request['session']
            bundle = request['name']
            self.sendMessage(json.dumps(self.getReply(self.db.getBundle(session, bundle))))
        elif type == 'DISCONNECTWARNING':
            self.sendMessage(json.dumps(self.getReply(None)))
        elif type == 'SAVEBUNDLE':
            self.sendMessage(json.dumps(self.getReply(None,msg='Save bundle not supported by this server')))
        elif type == 'SAVECONFIG':
            self.sendMessage(json.dumps(self.getReply(None, msg='Save configuration not supported by this server')))
        else:
            print 'NYI ' + type
            self.sendMessage(json.dumps(self.getError('NYI: {}'.format(type))))

    def getError(self, msg):
        res = OrderedDict()
        res['callbackID'] = self.callbackID
        status = OrderedDict()
        res['status'] = status
        status['type'] = 'ERROR'
        status['message'] = msg

        return res

    def getSuccessStatus(self, msg=''):
        status = OrderedDict()
        status['type'] = 'SUCCESS'
        status['message'] = msg
        return status

    def getReply(self, data, msg=''):
        res = OrderedDict()
        res['callbackID'] = self.callbackID
        if data:
            res['data'] = data
        res['status'] = self.getSuccessStatus(msg)
        return res

    def dataProtocol(self):
        data = OrderedDict()
        data['protocol'] = 'EMU-webApp-websocket-protocol'
        data['version'] = '0.0.2'
        return data
