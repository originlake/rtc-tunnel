#!/usr/bin/env python3

import argparse
import asyncio
import logging.handlers
import sys
import uuid

from rtc_tunnel import TunnelServer
from rtc_tunnel.signaling import WebSignaling, ConsoleSignaling


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ])


def main():
    parser = argparse.ArgumentParser(description='RTC Tunneling server')
    parser.add_argument('--source-name', '-S', help='Source name', default='server')
    parser.add_argument('--use-console-signal', '-c', help='Enable console signal server instead of web', action='store_true')
    parser.add_argument('--signal-url', '-u', help='Signal server send url', default='ws://127.0.0.1:9000/peerjs')
    parser.add_argument('--key', '-k', help='peerjs server key', default="peerjs")
    args = parser.parse_args()

    if not args.use_console_signal:
        signal_server = WebSignaling(args.source_name, args.signal_url, args.key, str(uuid.uuid4()))
    else:
        signal_server = ConsoleSignaling(args.source_name)
    server = TunnelServer(signal_server)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(server.run_async())
    except KeyboardInterrupt:  # CTRL+C pressed
        pass
    finally:
        loop.run_until_complete(server.close_async())
        loop.close()

if __name__ == '__main__':
    main()
