# RTC Tunnel

This project uses WebRTC protocol to establish socket tunnel between two hosts.

It was created to cover following use case:
I wanted to SSH connect to Raspberry PI that was in different network that my local PC.
Both networks are behind a NAT, so it's not so easy to create direct connection without help of third, publicly visible server that would serve as reverse SSH tunnel.

I decided to write this simple python application that uses WebRTC to establish p2p connection between two hosts and allows to tunnel any socket connection (not only SSH on 22).

Note, that this is not production ready solution. It's more like a Proof of concept that such connection may be possible.

Also note, that it is not always possible to establish p2p connection in WebRTC protocol, but for most common cases it works ok. And it's possible to solve this problem if you have access to TURN server.

You will also need publicly available signalling server, although it's used only to exchange few text messages at the beginning of communication. It's load is nothing compared to reverse SSH tunnel


## Install

This project `python>=3.7` and few dependencies that can be added using
```
pip3 install .
```
Note that it is using [aiortc](https://github.com/aiortc/aiortc) library, and you may have problems installing it on the Windows.
At least I had quite a few problems and decided to stick with Windows 10 Ubuntu WSL, which works like a charm .


## Run locally without signaling server

By default, both client and server will use console as signaling server.
That means you will be asked to copy and paste manually some json messages from client to server and back to make it running.

On server (ex. RaspberryPI):
```
rtc_server -c
```

On client (ex. PC):
```
rtc_client -c -s 3334 -d 22
```

On client (PC), port `3334` will be opened and will listen for new connections. Each connection will be redirected to port `22` on server (RaspberryPI).

Run on client (PC):
```
ssh -p 3334 pi@localhost
```


## Run with docker
Project [peerjs-server](https://github.com/peers/peerjs-server) contains web signaling server that can be used to communicate between two hosts.

On host that is available from both client (PC) and server (RaspberryPI) run peerjs-server application.
(For testing purposes this can be PC if Raspberry and PC are in the same network)
```
docker run -p 9000:9000 peerjs/peerjs-server -k <connection-key>
```

 The signal server is available at `ws://<peerjs-server-host>:9000`

On server (ex. RaspberryPI):
```
docker run --net=host originlake/rtc_tunnel:server -u ws://<peerjs-server-host>:9000 -k <connection-key>
```

On client (ex. PC):
```
docker run -p 3334:3334 originlake/rtc_tunnel:client -s 3334 -d 22 -u ws://<peerjs-server-host>:9000 -k <connection-key>
```

On client (PC), port `3334` will be opened and will listen for new connections. Each connection will be redirected to port `22` on server (RaspberryPI).

Run on client (PC):
```
ssh -p 3334 pi@localhost
```
