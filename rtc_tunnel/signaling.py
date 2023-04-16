import asyncio
import json
import sys
import websockets
import requests
from json import JSONDecodeError

from aiortc import RTCSessionDescription, RTCIceCandidate
from aiortc.sdp import candidate_from_sdp, candidate_to_sdp


class ConsoleSignaling:
    def __init__(self, source: str):
        self._source = source
        self._read_pipe = sys.stdin
        self._read_transport = None
        self._reader = None
        self._write_pipe = sys.stdout

    async def connect_async(self):
        loop = asyncio.get_event_loop()
        self._reader = asyncio.StreamReader(loop=loop)
        self._read_transport, _ = await loop.connect_read_pipe(
            lambda: asyncio.StreamReaderProtocol(self._reader),
            self._read_pipe)

    async def close_async(self):
        if self._reader is not None:
            self._read_transport.close()

    async def receive_async(self):
        print('-- Please enter a message from remote party to [%s] --' % self._source)
        while True:
            data = await self._reader.readline()
            try:
                message = data.decode(self._read_pipe.encoding)
                obj, source = object_from_string(message)
                print()
                return obj, source
            except JSONDecodeError:
                pass

    async def send_async(self, descr, dest: str):
        print('-- Please send this message to the remote party named [%s] --' % dest)
        message = object_to_string(descr, self._source)
        self._write_pipe.write(message + '\n')
        print()


class WebSignaling:
    def __init__(self, source: str, host_url: str, key: str, token: str, ping_interval: int = 20):
        self._source = source
        self._host_url = f"{host_url}/peerjs?key={key}&id={source}&token={token}"
        self._client = None
        self._ping_timer = None
        self._ping_interval = ping_interval

    async def connect_async(self):
        self._client = await websockets.connect(self._host_url, ping_interval=None)
        self._ping_timer = asyncio.ensure_future(self.send_heartbeat())
        # skip one for server confirmation
        await self._client.recv()

    async def close_async(self):
        if self._client is not None:
            await self._client.close()
        if self._ping_timer is not None:
            self._ping_timer.cancel()

    async def receive_async(self):
        message = await self._client.recv()
        return object_from_string(message)

    async def send_async(self, descr, dest: str):
        message = object_to_string(descr, dest)
        await self._client.send(message)

    async def send_heartbeat(self,):
        while self._client.open:
            await self._client.send(json.dumps({"type":"HEARTBEAT"}))
            await asyncio.sleep(self._ping_interval)


def get_peer_id(url: str):
    if url.startswith('ws://'):
        url = url.replace('ws://', 'http://')
    elif url.startswith('wss://'):
        url = url.replace('wss://', 'https://')
    res = requests.get(f'{url}/peerjs/id')
    if res.ok:
        return res.content.decode()
    else:
        return None

def object_to_string(obj, dest: str):
    if isinstance(obj, RTCSessionDescription):
        payload = {
            'sdp': obj.sdp,
            'type': obj.type
        }
        type = 'OFFER'
    elif isinstance(obj, RTCIceCandidate):
        payload = {
            'candidate': 'candidate:' + candidate_to_sdp(obj),
            'id': obj.sdpMid,
            'label': obj.sdpMLineIndex,
            'type': 'candidate',
        }
        type = 'CANDIDATE'
    else:
        raise ValueError('Can only send RTCSessionDescription or RTCIceCandidate')
    message = {
        'dst': dest,
        'payload': payload,
        'type': type
    }
    return json.dumps(message, sort_keys=True)


def object_from_string(message_str):
    obj = json.loads(message_str)
    if obj["type"] in ["OFFER", "CANDIDATE"]:
        payload = obj['payload']
        source = obj['src']
        dst = obj['dst']

        if payload['type'] in ['answer', 'offer']:
            return RTCSessionDescription(**payload), source
        elif payload['type'] == 'candidate':
            candidate = candidate_from_sdp(payload['candidate'].split(':', 1)[1])
            candidate.sdpMid = payload['id']
            candidate.sdpMLineIndex = payload['label']
            return candidate, source
    return obj["type"], None

