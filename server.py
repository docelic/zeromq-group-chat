import argparse
import zmq

# Implements chat server
class ChatServer():

  def __init__(self, client_send_port, client_recv_port, host):
    self.host = host
    self.client_send_port = client_send_port
    self.client_recv_port = client_recv_port

    self.context = zmq.Context()

    # Interface to be listening for users' incoming messages, 1:1
    self.recv_socket = self.context.socket(zmq.REP)
    self.recv_socket.bind('tcp://{}:{}'.format(self.host, self.client_send_port))

    # Interface to be publishing group messages to, 1:N
    self.send_socket = self.context.socket(zmq.PUB)
    self.send_socket.bind('tcp://{}:{}'.format(self.host, self.client_recv_port))

    # We can do this in the single/main thread since there's only one thing we need to read,
    # so we can block freely.
    while True:
      # Wait for users' incoming messages
      data = self.recv_socket.recv_json()
      print(data)

      # Confirm receipt and distribute message to everyone (including the client who sent it)
      self.recv_socket.send(b'\x00')
      self.send_socket.send_json(data)

# Executes when the script is started; reads args and starts chat server
try:
  parser = argparse.ArgumentParser(description='Run chat server')
  parser.add_argument('client_send_port', type=str, help='Port clients PUB to', default=6000, nargs='?')
  parser.add_argument('client_recv_port', type=str, help='Port clients SUB to', default=7000, nargs='?')
  parser.add_argument('host', type=str, help='Host/IP to bind to', nargs='?')
  args = parser.parse_args()

  server = ChatServer(
		args.client_send_port or 6000,
		args.client_recv_port or 7000,
		args.host or 0
	)
except KeyboardInterrupt as e:
  pass
except:
  raise
