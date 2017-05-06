import argparse
import os.path
import sys

import daemonize

from Settings import get_setting, load_settings


def run_server():
    from twisted.python import log
    from twisted.internet import reactor
    from autobahn.twisted.websocket import WebSocketServerFactory
    from EmuServer import EmuServerProtocol

    if get_setting('logFile'):
        f = open(get_setting('logFile'), 'a')
        log.startLogging(f)
    else:
        log.startLogging(sys.stdout)

    factory = WebSocketServerFactory()
    factory.protocol = EmuServerProtocol

    reactor.listenTCP(get_setting('port'), factory)
    reactor.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='EMU-webApp server program')
    parser.add_argument('settings', help='Settings file', nargs='?')

    args = parser.parse_args()

    if args.settings:
        load_settings(args.settings)

    if get_setting('daemonize'):
        d = daemonize.Daemonize(app=os.path.basename(sys.argv[0]), pid=get_setting('pid'), action=run_server)
        d.start()
    else:
        run_server()
