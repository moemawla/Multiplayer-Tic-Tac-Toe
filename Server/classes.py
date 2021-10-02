import socket
import json

class Player():
    """A class that represents a tic-tac-toe player.

    Attributes:
        name: A string representing the player name.
    """

    def __init__(self, name):
        """Initializes the Player class."""
        self.name = name

class Client(Player):
    """A class that represents a client connecting to the server.

    This class extends the Player class.

    Attributes:
        name: A string representing the player name. Inherited from the Player class.
        connection: An object representing the socket connection linked to the client.
        address: A tuple containing the client's IP address and the port number.
    """

    def __init__(self, name, connection, address):
        """Initializes the Client class.

        Args:
            name: A string representing the player name. Passed to the Player class constructor.
            connection: An object representing the socket connection linked to the client.
            address: A tuple containing the client's IP address and the port number.
        """
        super().__init__(name)
        self.connection = connection
        self.address = address

class Game():
    """A class that represents a tic-tac-toe game.

    This class is responsible for keeping track of the game progress, validating the players' choices
    and detecting if the game ended by a win or a tie.

    Attributes:
        player_1: An instance of the Player class representing the first player.
        player_2: An instance of the Player class representing the second player.
        winner: A reference to the winning player instance if the game is won. Default value is None.
        ended: A boolean indicating if the game has ended. Default value is False.
        board: A list of 3 lists each with 3 elements. Represents the game board. Default value for the elements is a single space.
        BOARD_DIMENSION: A constant integer indicating the height and width of the board.
        WIN_MAP: A constant tuple containing the cell-coordinates of all the possible scenarios for a win.
    """

    BOARD_DIMENSION = 3
    WIN_MAP = (
        ((0,0), (0,1), (0,2)),
        ((1,0), (1,1), (1,2)),
        ((2,0), (2,1), (2,2)),
        ((0,0), (1,0), (2,0)),
        ((0,1), (1,1), (2,1)),
        ((0,2), (1,2), (2,2)),
        ((0,0), (1,1), (2,2)),
        ((0,2), (1,1), (2,0))
    )

    def __init__(self, player_1, player_2):
        """Initializes the Game class.

        Validates that player_1 and player_2 are instances of the Player class and are not referring to the same instance.

        Args:
            player_1: An instance of the Player class representing the first player.
            player_2: An instance of the Player class representing the second player.

        Raises:
            ValueError: If the arguments provided for both players are not valid.
        """
        if (not isinstance(player_1, Player)) or (not isinstance(player_2, Player)) or (player_1 == player_2):
            raise ValueError('Invalid players provided!')

        self.player_1 = player_1
        self.player_2 = player_2
        self.winner = None
        self.ended = False
        self.board = [
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' ']
        ]

    def validate_board(self, updated_board):
        """Validates that the passed argument contains exactly 1 valid update on the board.

        Args:
            updated_board: A list of 3 lists representing the updated game-board.
        
        Returns:
            A tuple containing 2 integers between 0 and 2 inclusive.
            These integers represent the row and column indices, respectively, of the changed cell.
            For example:
                (0, 2)
        
        Raises:
            ValueError: If the updated board has a wrong structure, if a non-empty cell is updated or if multiple cells are updated.
        """
        number_of_changes = 0
        changed_cell = None

        if (not isinstance(updated_board, list)) or len(updated_board) != self.BOARD_DIMENSION:
            raise ValueError('The provided board is corrupted!')

        for row_index, row in enumerate(updated_board):
            if (not isinstance(row, list)) or len(row) != self.BOARD_DIMENSION:
                raise ValueError('The provided board is corrupted!')
            for column_index, value in enumerate(row):
                if value != self.board[row_index][column_index]:
                    if self.board[row_index][column_index] != ' ':
                        raise ValueError('Non-empty cell was updated!')
                    number_of_changes += 1
                    changed_cell = (row_index, column_index)
        
        if number_of_changes != 1:
            raise ValueError('Multiple cells updated!')
        
        return changed_cell

    def validate_player(self, player):
        """Validates that the passed argument refers to one of the game players.

        Args:
            player: An instance of the Player class.

        Raises:
            ValueError: If the passed argument does not refer to one of the game players.
        """
        if (player != self.player_1) and (player != self.player_2):
            raise ValueError('Unknown player provided!')

    def process(self, player, updated_board):
        """Processes the player's update on the board.

        Processes the player's update by performing the following:
            - calls the validate methods on both passed arguments.
            - retrieves the coordinates of the changed cell.
            - updates the game board at the changed cell with the right value (X/O).
            - marks the game as ended if there is either a win or a tie.

        Args:
            player: An instance of the Player class. Represents the current player.
            updated_board: A list of 3 lists representing the game-board updated by the player.

        Raises:
            ValueError: If either of the 2 passed arguments is not valid.
        """
        self.validate_player(player)

        # validate the updated board and retrieve the coordinates of the changed cell
        updated_row, updated_column = self.validate_board(updated_board)
        
        # update the game board at the changed cell with the player's token ( X/O)
        self.board[updated_row][updated_column] = self.get_player_token(player)
        
        # check if there is a win or a tie and mark the game as ended
        if self.is_a_win() or self.is_a_tie():
            self.ended = True

    def is_a_win(self):
        """Checks if the game is won.
        
        Loops over all the possible winning scenarios from the WIN_MAP class constant.
        If a winning scenario is found, updates the winner attribute with the correct player based on the token value (X/O).

        Returns:
            A boolean representing whether the game is won.
        """
        for scenario in self.WIN_MAP:
            value_1 = self.board[scenario[0][0]][scenario[0][1]]
            value_2 = self.board[scenario[1][0]][scenario[1][1]]
            value_3 = self.board[scenario[2][0]][scenario[2][1]]
            if value_1 == value_2 == value_3 != ' ':
                self.winner = self.get_player_from_token(value_1)
                return True
        return False

    def is_a_tie(self):
        """Checks if the game has ended in a tie.
        
        Checks a game tie by making sure there are no empty cells left.

        Returns:
            A boolean representing whether the game is a tie.
        """
        for row in self.board:
            for cell in row:
                if cell == ' ':
                    return False
        return True

    def get_player_token(self, player):
        """Returns the token belonging to the passed player.

        Args:
            player: An instance of the Player class.

        Returns:
            A single-character string that represents the value of the token belonging to the passed player.
            If the player is player_1, the token is X.
            If the player is player_2, the token is O.

        Raises:
            ValueError: If the passed argument does not refer to one of the game players.
        """
        self.validate_player(player)

        if player == self.player_1:
            return 'X'
        return 'O'

    def get_player_from_token(self, value):
        """Returns the player who is the owner of the passed token value.

        Args:
            value: A single-character string representing the token value.

        Returns:
            An instance of the Player class refering to one of the two game players.
            If the token is X, the player is player_1.
            If the token is O, the player is player_2.

        Raises:
            ValueError: If the passed argument does not equal X or O.
        """
        if value == 'X':
            return self.player_1
        elif value == 'O':
            return self.player_2
        else:
            raise ValueError('Wrong cell value provided!')

class Server():
    """A class that represents the server of the game.

    This class is responsible for the following:
        - accepting client connections.
        - staring the game when 2 clients connect.
        - managing the game session.
        - managing the players' turns.
        - sending/receiving messages to/from connected clients.

    Attributes:
        socket: An instance of the socket class. Default value is None.
        clients: A list containing instances of the Client class.
        current_player: An instance of the Client class. Default value is None.
        PORT: A constant integer representing the port number which the socket will be bound to.
    """

    PORT = 65432

    def __init__(self):
        """Initializes the Server class."""
        self.socket = None
        self.clients = []
        self.current_player = None

    def run(self):
        """Runs the game session.

        Performs the following actions:
            - Initializes the socket object and binds it to any ip address and the port number represented by the constant PORT.
            - accepts the client connections.
            - starts the game.
            - closes the socket at the end of the session.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('', self.PORT))
            self.accept_clients()
            print(f'{len(self.clients)} clients are now connected')
            print('Starting the game')
            self.play_game()
        except KeyboardInterrupt:
            print('Bye!')
        except Exception as e:
            print(e)
        finally:
            for player in self.clients:
                self.send_message_to_player(player, 'Server stopped!')
            self.socket.close()

    def accept_clients(self):
        """listens to and accepts 2 client connections.

        Runs only if the socket is initialized.

        Each accepted connection is created as a Client object and added to the clients list attribute.
        """
        if not self.socket:
            return

        self.socket.listen()
        print(f'Listening for incoming connections on port {self.PORT}')

        while len(self.clients) < 2:
            connection, address = self.socket.accept()
            player = Client(f'Player {len(self.clients) + 1}', connection, address)
            print(f'{player.name} connected by {player.address}')
            self.clients.append(player)
            if len(self.clients) == 1:
                self.send_message_to_player(player, 'Welcome! Waiting for a second player to join')
            else:
                self.send_message_to_player(player, 'Welcome!')

    def play_game(self):
        """Starts and plays the game.

        Plays the game in iterations as follows:
            - determines the current player.
            - sends a message to the next player informing the player to wait.
            - sends the current board to the current player and gets the updated board back.
            - calls the process method from the Game instance and checks if the game ended.
            - if the game has ended, stops the game and sends the results to the players.
            - if the game has not ended, switches players' turns and continues to the next iteration.
        """
        self.current_player = self.clients[0]
        game = Game(self.current_player, self.next_player)
        
        # Inform the players that the game has started
        for player in self.clients:
            self.send_message_to_player(player, 'START')

        while True:
            # inform the next player that it is his opponent's turn
            self.send_message_to_player(self.next_player, 'WAIT')

            # send the current game board to the current player and get the updated board back
            json_board = json.dumps(game.board)
            updated_board = self.get_updated_board(self.current_player, json_board)

            # check if the player sent nothing back, which means the player has disconnected
            if not updated_board:
                print(f'{self.current_player.name} disconnected')
                self.send_message_to_player(self.next_player, 'Oops! Your opponent disconnected')
                return

            try:
                # let the game process the updated board and check if the game has ended
                game.process(self.current_player, updated_board)
                if game.ended:
                    break
            except Exception as e:
                # unexpected exception and the game must be stopped
                print(f'Faced error during {self.current_player.name}\'s turn: ', e)
                for player in self.clients:
                    self.send_message_to_player(player, 'Oops! Game crashed')
                return

            self.change_turn()

        self.send_game_results(game.winner)

    def change_turn(self):
        """Sets the current_player attribute to point to the next player."""
        self.current_player = self.next_player

    @property
    def next_player(self):
        """Returns a Client instance that represents the non-current player."""
        if self.clients[0] == self.current_player:
            return self.clients[1]
        return self.clients[0]

    def get_updated_board(self, player, json_board):
        """Retrieves the updated board from the player.

        Args:
            player: An instance of the Client class representing a player.
            json_board: A JSON string-representaion of the game board to be sent to the player.

        Returns:
            A list representing the updated board retrieved from the player. None if the player has disconnected.
        """
        # send the current game board to the player
        self.send_message_to_player(player, json_board)

        # recieve the updated board from the player
        connection = player.connection
        input = connection.recv(1024)

        # check if the client has disconnected and return None
        if not input:
            return None
        
        # decode the message sent from player, which should be a JSON string-representation of the updated board
        input = input.decode('utf-8')
        print(f'{player.name} sent this message:')
        print(input)
        return json.loads(input)

    def send_message_to_player(self, player, message):
        """Adds a delimiter to the end of the message and sends it to the player.

        Args:
            player: An instance of the Client class representing a player.
            message: A string to be sent to the player.
        """
        message = f'{message}-'
        player.connection.sendall(bytes(message, 'utf-8'))

    def send_game_results(self, winner):
        """Sends the game results to the players.

        Args:
            winner: An instance of the Client class representing the winner. None if the game was not won.
        """
        if winner:
            print(f'{winner.name} Won')
        else:
            print('It is a tie')

        for client in self.clients:
            if not winner:
                self.send_message_to_player(client, 'TIE')
            elif winner == client:
                self.send_message_to_player(client, 'WON')
            else:
                self.send_message_to_player(client, 'LOST')
