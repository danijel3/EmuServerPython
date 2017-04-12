import sys
from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory
from EmuServer import EmuServerProtocol
import Settings

if __name__ == '__main__':

    if len(sys.argv) > 1:
        Settings.load_settings(sys.argv[1])

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory()
    factory.protocol = EmuServerProtocol

    reactor.listenTCP(Settings.settings['port'], factory)
    reactor.run()
