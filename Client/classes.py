import socket
import json
import os
import re

class GameHelper:
    """A class that helps the client to playe the tic-tac-toe game over the network.

    This class is responsible for:
        - validating the game board.
        - printing the board in the terminal.
        - asking the user to fill a cell and validating the choice.

    Attributes:
        ALLOWED_COORDINATES: A constant set containing the allowed row and column coordinates to be entered by the user.
        BOARD_DIMENSION: A constant integer indicating the height and width of the board.
    """
    ALLOWED_COORDINATES = {'0', '1', '2'}
    BOARD_DIMENSION = 3

    def validate_board(self, board):
        """Validates the board.

        Args:
            board: A list of 3 lists each with 3 elements. Represents the game board.

        Raises:
            ValueError: If the provided board does not have the correct structure.
        """
        if (not isinstance(board, list)) or len(board) != self.BOARD_DIMENSION:
            raise ValueError('The provided board is corrupted!')
        for row in board:
            if (not isinstance(row, list)) or len(row) != self.BOARD_DIMENSION:
                raise ValueError('The provided board is corrupted!')

    def get_coordinates_from_user(self):
        """Retrievs the coordinates, of the cell to be filled, from the user.

        Makes sure the coordinates are valid and keeps asking the user for coordinates until the user enters valid ones.

        Returns:
            A tuple containing 2 integers between 0 and 2 inclusive.
            These integers represent the row and column indices, respectively, of the changed cell.
        """
        try:
            while True:
                coordinates = input('Which cell you want to fill? ')
                if (len(coordinates) == 2) and (coordinates[0] in self.ALLOWED_COORDINATES) and (coordinates[1] in self.ALLOWED_COORDINATES):
                    return (int(coordinates[0]), int(coordinates[1]))
                print('Only 0, 1 and 2 are allowed for row and column coordinates')
        except KeyboardInterrupt:
            return None

    def print_board(self, board):
        """Prints the board to the terminal.

        Calls the validate_board method before printing the board.

        Args:
            board: A list of 3 lists each with 3 elements. Represents the game board.

        Raises:
            ValueError: If the provided board does not have the correct structure.
        """
        self.validate_board(board)
        os.system('clear')
        for row_index, row in enumerate(board):
            print(row[0], '|', row[1], '|', row[2])
            if row_index != 2:
                print('--|---|--')

    def get_updated_board(self, board):
        """Updates the board based on the user's choice.

        This method does the following:
            - calls the validate_board method.
            - calls the print_board method.
            - calls the get_coordinates_from_user method.
            - makes sure the chosen coordinates don't point to a non-empty cell.
            - if the coordinates point to an empty cell, updates the board and returns it.

        Args:
            board: A list of 3 lists each with 3 elements. Represents the game board.
        
        Returns:
            A list representing the updated board.
        """
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
    """A class that represents the client of the game.

    This class is responsible for the following:
        - connecting to the game server.
        - recieving and processing server messages.
        - coordinating with the server to play during the user's turn.
        - utilizing the GameHelper class to translate user's commands into a valid board to be passed back to the server.

    Attributes:
        socket: An instance of the socket class.
        play_game: A boolean that represents whether the game can be played or not. Used as a status flag.
        SERVER_PORT: A constant integer representing the port number which the server socket will be listening on.
    """
    SERVER_PORT = 65432

    def __init__(self):
        """Initializes the Client class."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.play_game = False

    def run(self):
        """Connects to the game server and starts the game when the server sends the right signal.

        This method does the following:
            - calls the get_server_address method.
            - connects the socket to the server.
            - receives messages from the server and calls the process_server_message method.
            - checks the play_game attribute to decide whether to start playing.
            - closes the socket at the end of the session.
        """
        try:
            # ask the user for the server ip and connect the socket to the server
            self.socket.connect((self.get_server_address(), self.SERVER_PORT))

            # read messages from the server and wait for the game to begin
            while True:
                received_message = self.socket.recv(1024)
                received_message = received_message.decode('utf-8')
                self.process_server_message(received_message)
                if self.play_game:
                    break

            # start playing the game
            self.play()
        except KeyboardInterrupt:
            os.system('clear')
            print('Bye!')
        except Exception as e:
            print(e)
        finally:
            self.socket.close()

    def play(self):
        """Plays the game on the client side.

        This method does the following:
            - keeps listening for server messages.
            - calls the process_server_message method.
            - checks if play_game attribute is False and quits the game.
            - utilizes the GameHelper class to get the updated board from the user during the user's turn.
            - checks if no board was returned by the GameHelper and quits the game.
            - sends the updated board back to the server.
        """
        game_helper = GameHelper()

        # keep listening for server messages and process each message
        while True:
            received_message = self.socket.recv(1024)
            received_message = received_message.decode('utf-8')

            # process the message received from the server
            board = self.process_server_message(received_message)

            # the processed message signaled an end to the game
            if not self.play_game:
                print('Game ended')
                return

            # the message received from the server did not signal an end to the game
            # but was not the board either
            if not board:
                continue
            
            # get the updated board from the user
            updated_board = game_helper.get_updated_board(board)

            # the user decided to quit
            if not updated_board:
                os.system('clear')
                print('Bye!')
                return

            # send the updated board back to the server
            json_board = json.dumps(updated_board)
            self.socket.sendall(bytes(json_board, 'utf-8'))

    def get_server_address(self):
        """Asks the user for the server's ip address.

        Keeps asking the user for the server's ip address until a valid ip is provided.

        Returns:
            A string representing a valid ip address.
        """
        print('What is the server ip address?')
        while True:
            ip_address = input()
            # regular expression to validate IP addresses
            regex = '^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$'
            if re.search(regex, ip_address):
                return ip_address
            print('Invalid ip adress provided. Please try again:')


    def process_server_message(self, server_message):
        """Processes messgaes received from the server.

        Args:
            server_message: A string representing 1 or more messages received from the server. 

        Returns:
            A list representing the game board if the server message was a board. None otherwise.
        """
        # split the messages by - as the delimiter
        messages = server_message.split('-')
        
        for message in messages:
            # skipping the empty message after the last delimiter
            if not message:
                continue

            # checking first if the message is the game board
            try:
                board = json.loads(message)
                if isinstance(board, list):
                    return board
            except:
                # the message was not a JSON
                pass
            
            # processing messages that do not contain the board
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
