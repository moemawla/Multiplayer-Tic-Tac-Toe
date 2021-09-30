import socket
import json
import os
import re

class GameHelper:
    ALLOWED_COORDINATES = {'0', '1', '2'}
    BOARD_DIMENSION = 3

    def validate_board(self, board):
        if (not isinstance(board, list)) or len(board) != self.BOARD_DIMENSION:
            raise ValueError('The provided board is corrupted!')
        for row in board:
            if (not isinstance(row, list)) or len(row) != self.BOARD_DIMENSION:
                raise ValueError('The provided board is corrupted!')

    def get_coordinates_from_user(self):
        try:
            while True:
                coordinates = input('Which cell you want to fill? ')
                if (len(coordinates) == 2) and (coordinates[0] in self.ALLOWED_COORDINATES) and (coordinates[1] in self.ALLOWED_COORDINATES):
                    return (int(coordinates[0]), int(coordinates[1]))
                print('Only 0, 1 and 2 are allowed for row and column coordinates')
        except KeyboardInterrupt:
            return None

    def print_board(self, board):
        self.validate_board(board)
        os.system('clear')
        for row_index, row in enumerate(board):
            print(row[0], '|', row[1], '|', row[2])
            if row_index != 2:
                print('--|---|--')

    def get_updated_board(self, board):
        self.validate_board(board)
        self.print_board(board)
        while True:
            input = self.get_coordinates_from_user()
            if not input:
                return None

            row, column = input
            if board[row][column] != ' ':
                print('Please choose an empty cell!')
                continue

            # it doesn't matter what we fill the cell with
            # the server will replace it with the correct value for each player
            board[row][column] = '#'
            return board

class Client():
    SERVER_PORT = 65432

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.play_game = False

    def run(self):
        self.socket.connect((self.get_server_address(), self.SERVER_PORT))

        while True:
            received_message = self.socket.recv(1024)
            received_message = received_message.decode('utf-8')
            self.process_server_message(received_message)
            if self.play_game:
                break

        try:
            self.play()
        except KeyboardInterrupt:
            os.system('clear')
            print('Bye!')
        except Exception as e:
            print(e)
        finally:
            self.socket.close()

    def play(self):
        game_helper = GameHelper()
        while True:
            received_message = self.socket.recv(1024)
            received_message = received_message.decode('utf-8')
            board = self.process_server_message(received_message)

            if not self.play_game:
                print('Game ended')
                return

            if not board:
                continue
            
            updated_board = game_helper.get_updated_board(board)
            if not updated_board:
                os.system('clear')
                print('Bye!')
                break

            json_board = json.dumps(updated_board)
            self.socket.sendall(bytes(json_board, 'utf-8'))

    def get_server_address(self):
        print('What is the server ip address?')
        while True:
            ip_address = input()
            # regular expression to validate IP addresses
            regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
            if re.search(regex, ip_address):
                return ip_address
            print('Invalid ip adress provided. Please try again:')


    def process_server_message(self, server_message):
        messages = server_message.split('-')
        
        for message in messages:
            if not message:
                # skipping the empty message after the last delimiter
                continue

            # checking first if the message is the game board
            try:
                board = json.loads(message)
                if isinstance(board, list):
                    return board
            except:
                # the message was not a JSON
                pass
            
            if message == 'START':
                self.play_game = True
                print('Game started!')
            elif message == 'WAIT':
                print('Your opponent\'s turn')
            elif message == 'WON':
                self.play_game = False
                print('Congrats! You won!')
            elif message == 'LOST':
                self.play_game = False
                print('Better luck next time')
            elif message == 'TIE':
                self.play_game = False
                print('It is a tie!')
            else:
                self.play_game = False
                print(message)
