import socket
import json
import os

class Game:
    ALLOWED_COORDINATES = {'0', '1', '2'}
    BOARD_DIMENSION = 3

    def validate_board(self, board):
        if (not isinstance(board, list)) or len(board) != self.BOARD_DIMENSION:
            raise ValueError('The provided board is corrupted!')
        for row_index, row in enumerate(board):
            if (not isinstance(row, list)) or len(row) != self.BOARD_DIMENSION:
                raise ValueError('The provided board is corrupted!')

    def get_coordinates_from_user(self):
        coordinates = None
        while True:
            coordinates = input('Which cell you want to fill? ')
            if (len(coordinates) == 2) and (coordinates[0] in self.ALLOWED_COORDINATES) and (coordinates[1] in self.ALLOWED_COORDINATES):
                return (int(coordinates[0]), int(coordinates[1]))
            print('Only 0, 1 and 2 are allowed for row and column coordinates')

    def print_board(self, board):
        self.validate_board(board)
        os.system("clear")
        for row in board:
            print(row[0], '|', row[1], '|', row[2])
            print('--|---|--')

    def get_updated_board(self, board):
        self.validate_board(board)
        self.print_board(board)
        row, column = self.get_coordinates_from_user()
        board[row][column] = '#'
        return board
class Client():
    SERVER_PORT = 65432

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.continue_game = True

    def run(self):
        self.socket.connect(('127.0.0.1', self.SERVER_PORT))
        try:
            self.play_game()
        except Exception as e:
            print(e)
        finally:
            self.socket.close()

    def process_server_message(self, message):
        try:
            board = json.loads(message)
            if isinstance(board, list):
                return
        except:
            pass

        if 'WON' == message:
            self.continue_game = False
            print('Congrats! You won!')
        elif 'LOST' == message:
            self.continue_game = False
            print('Better luck next time')
        elif 'TIE' == message:
            self.continue_game = False
            print('It is a tie!')
        else:
            self.continue_game = False
            print('An issue has occured')
            print(repr(message))

    def play_game(self):
        game = Game()
        while True:
            received_message = self.socket.recv(1024)
            received_message = received_message.decode("utf-8")
            self.process_server_message(received_message)
            if not self.continue_game:
                break
            
            board = json.loads(received_message)
            updated_board = game.get_updated_board(board)
            json_board = json.dumps(updated_board)
            self.socket.sendall(bytes(json_board, 'utf-8'))
