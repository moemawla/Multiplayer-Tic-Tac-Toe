import socket

class Client():
    SERVER_PORT = 65432

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect(('127.0.0.1', self.SERVER_PORT))

        message_to_send = input('What would you like to send to the server? \n')
        self.socket.sendall(bytes(message_to_send, 'utf-8'))

        received_message = self.socket.recv(1024)
        print('You received from the server this message:')
        print(repr(received_message))

        self.socket.close()
