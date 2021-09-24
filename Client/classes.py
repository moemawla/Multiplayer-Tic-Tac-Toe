import socket
import json

class Client():
    SERVER_PORT = 65432

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect(('127.0.0.1', self.SERVER_PORT))

        received_message = self.socket.recv(1024)
        print('You received from the server this message:')
        print(repr(received_message))

        board = [
            ['X', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' ']
        ]
        board = json.dumps(board)
        self.socket.sendall(bytes(board, 'utf-8'))
        self.socket.close()
