#!/usr/bin/env python3

import argparse
import asyncio
import logging.handlers
import sys
import uuid
import websockets

from rtc_tunnel import TunnelClient
from rtc_tunnel.signaling import WebSignaling, ConsoleSignaling


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ])

logging.getLogger("aiortc").setLevel(logging.WARNING)
logging.getLogger("aioice").setLevel(logging.WARNING)

def main():
    parser = argparse.ArgumentParser(description='RTC Tunneling client')
    parser.add_argument('--destination-port', '-d', help='Destination port', default=22)
    parser.add_argument('--source-port', '-s', help='Source port', default=3334)
    parser.add_argument('--source-name', '-S', help='Source name', default='client')
    parser.add_argument('--destination-name', '-D', help='Destination name', default='server')
    parser.add_argument('--use-console-signal', '-c', help='Enable console signal server instead of web', action='store_true')
    parser.add_argument('--signal-url', '-u', help='Signal server send url', default='ws://127.0.0.1:9000/peerjs')
    parser.add_argument('--key', '-k', help='peerjs server key', default="peerjs")
    args = parser.parse_args()

    if not args.use_console_signal:
        signal_server = WebSignaling(args.source_name, args.signal_url, args.key, str(uuid.uuid4()))
    else:
        signal_server = ConsoleSignaling(args.source_name)
    client = TunnelClient('', args.source_port, args.destination_port, signal_server, args.destination_name)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(client.run_async())
    except KeyboardInterrupt:  # CTRL+C pressed
        pass
    except websockets.exceptions.ConnectionClosedError:
        logging.info("[ERROR] Connection closed by the signal server, please verify the key")
    finally:
        loop.run_until_complete(client.close_async())
        loop.close()

if __name__ == '__main__':
    main()
