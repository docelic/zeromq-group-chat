# zeromq-group-chat

Simplest possible group chat implemented using ZeroMQ.

Uses a central server to which all users connect.

Implements chat using 2 ZeroMQ sockets:

- One REQ-REP for submitting new messages to the server
- One PUB-SUB for distributing messages from the server to all connected clients

## Client

```
python3 client.py [nickname] [host] [send_port] [recv_port]
```

For messages from local user the client simply reads lines from
the terminal in the usual cooked mode. Readline or similar
library is not used, but you can run the application under
`rlwrap` to enable readline functionality.

## Server

```
python3 server.py [SEND_PORT] [RECV_PORT] [HOST]
```

The server simply waits for incoming messages and publishes
them to all connected subscribers / clients.

## ZeroMQ Details

The app uses a REQ-REP and a PUB-SUB socket.

Alternatively, submitting messages to the server could be
implemented using REQ or DEALER requests to the server's
ROUTER socket.

## Encryption

Encryption is not included. One could e.g. set up a double
ratchet encryption with https://github.com/tgalal/python-axolotl.
