import argparse
import zmq
import threading
import getpass

# Implements the client side of chat
class ChatClient():

  def __init__(self, username, host, send_port, recv_port):
    self.username = username
    self.host = host
    self.send_port = send_port
    self.recv_port = recv_port

    self.context = zmq.Context()

    # We're not using a poll mechanism in this version.
    #self.poller = zmq.Poller()
    self.connect_to_host()

    # Start a thread that's waiting for user's input and sending it to the chat server.
    sender = threading.Thread(target=self.sending_messages)
    sender.daemon = True
    sender.start()

    # Start a thread that's waiting for remote messages and displaying them in the local console.
    receiver = threading.Thread(target=self.receiving_messages)
    receiver.daemon = True
    receiver.start()

    # The usual threads cleanup; will happen when both threads exit. We don't provide a programmed
    # way to exit so it'll only happen on an Exception, since we don't handle Exceptions ourselves.
    # (It won't happen on Ctrl+c either, that uses a different code path.)
    sender.join()
    receiver.join()

  # Extracted into a separate function in case we want to easily add a reconnect method.
  # We could have separate hosts for REQ and SUB, but we use a single one here.
  def connect_to_host(self):
    self.send_socket = self.context.socket(zmq.REQ)
    connect_string = 'tcp://{}:{}'.format( self.host, self.send_port)
    self.send_socket.connect(connect_string)

    self.recv_socket = self.context.socket(zmq.SUB)
    self.recv_socket.setsockopt_string(zmq.SUBSCRIBE, '')
    connect_string = 'tcp://{}:{}'.format( self.host, self.recv_port)
    self.recv_socket.connect(connect_string)

    # Again, not using a poller but 2 threads. If we used a poller, we could
    # do e.g. `socks = dict(poller.poll())` from a single thread etc.
    #self.poller.register(self.recv_socket, zmq.POLLIN)
    #self.poller.register(self.send_socket, zmq.POLLIN)

  # Simple loop to keep receiving messages from the server and print them to the console.
  def receiving_messages(self):
    while True:
      data = self.recv_socket.recv_json() # Blocks
      print('{}: {}'.format(data['username'], data['message']))

  # Simple loop to keep reading messages from the console and send them to server.
  def sending_messages(self):
    while True:
      message = input() # Blocks
      self.send_socket.send_json({ 'username': self.username, 'message': message })
      self.send_socket.recv() # Every REQ needs to read its REP

# Executes when the script is started; reads args and starts chat client
try:
  parser = argparse.ArgumentParser(description='Run chat client')
  parser.add_argument('username', type=str, help='Username', nargs='?')
  parser.add_argument('host', type=str, help='Host/IP', nargs='?')
  parser.add_argument('send_port', type=str, help='Port clients PUB to', nargs='?')
  parser.add_argument('recv_port', type=str, help='Port clients SUB to', nargs='?')
  args = parser.parse_args()

  chat = ChatClient(
    args.username or getpass.getuser(),
		args.host or 0,
		args.send_port or 6000,
		args.recv_port or 7000
  )
except KeyboardInterrupt as e:
  pass
except:
  raise
