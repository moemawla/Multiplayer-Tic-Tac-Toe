import socket
import copy
import json

class Player():
    def __init__(self, name):
        self.name = name

class Client(Player):
    def __init__(self, name, connection, address):
        super().__init__(name)
        self.connection = connection
        self.address = address

class Game():
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
    
    def get_board_copy(self):
        return copy.deepcopy(self.board)

    def validate_board(self, updated_board):
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
        if (not self.player_1) or (not self.player_2):
            raise ValueError('Players are missing!')

        if (player != self.player_1) and (player != self.player_2):
            raise ValueError('Unknown player provided!')

    def process(self, player, updated_board):
        self.validate_player(player)
        updated_row, updated_column = self.validate_board(updated_board)
        self.board[updated_row][updated_column] = self.get_player_token(player)
        # check if there is a win or a tie and mark the game as ended
        if self.is_a_win() or self.is_a_tie():
            self.ended = True

    def is_a_win(self):
        for scenario in self.WIN_MAP:
            value_1 = self.board[scenario[0][0]][scenario[0][1]]
            value_2 = self.board[scenario[1][0]][scenario[1][1]]
            value_3 = self.board[scenario[2][0]][scenario[2][1]]
            if value_1 == value_2 == value_3 != ' ':
                self.winner = self.get_player_from_token(value_1)
                return True
        return False

    def is_a_tie(self):
        for row in self.board:
            for cell in row:
                if cell == ' ':
                    return False
        return True

    def get_player_token(self, player):
        self.validate_player(player)

        if player == self.player_1:
            return 'X'
        return 'O'

    def get_player_from_token(self, value):
        if value == 'X':
            return self.player_1
        elif value == 'O':
            return self.player_2
        else:
            raise ValueError('Wrong cell value provided!')

class Server():
    PORT = 65432

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.PORT))
        self.clients = []
        self.turn = 0

    def run(self):
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

        print(f'{len(self.clients)} clients are now connected')

        try:
            print('Starting the game')
            self.play_game()
        except Exception as e:
            print(e)
        finally:
            self.socket.close()

    def play_game(self):
        game = Game(self.clients[0], self.clients[1])
        
        for player in self.clients:
            self.send_message_to_player(player, 'START')

        while True:
            current_player = self.get_current_player()

            # inform the other player that it is his opponent's turn
            other_player = self.get_other_player(current_player)
            self.send_message_to_player(other_player, 'WAIT')

            json_board = json.dumps(game.get_board_copy())
            updated_board = self.get_player_move(current_player, json_board)

            if not updated_board:
                print(f'{current_player.name} disconnected')
                self.send_message_to_player(other_player, 'Oops! Your opponent disconnected')
                return

            try:
                game.process(current_player, updated_board)
                if game.ended:
                    break
            except Exception as e:
                # unexpected exception and the game must be stopped
                print(f'Faced error during {current_player.name}\'s turn: ', e)
                for player in self.clients:
                    self.send_message_to_player(player, 'Oops! Game crashed')
                return

            self.change_turn()

        self.send_game_results(game.winner)

    def change_turn(self):
        self.turn = 1 if self.turn == 0 else 0

    def get_current_player(self):
        return self.clients[self.turn]

    def get_other_player(self, player):
        if self.clients[0] == player:
            return self.clients[1]
        return self.clients[0]

    def get_player_move(self, player, data):
        self.send_message_to_player(player, data)

        connection = player.connection
        input = connection.recv(1024)
        if not input:
            return None
        
        input = input.decode('utf-8')
        print(f'{player.name} sent this message:')
        print(input)
        return json.loads(input)

    def send_message_to_player(self, player, message):
        connection = player.connection
        # add delimeter after the message
        message = f'{message}-'
        connection.sendall(bytes(message, 'utf-8'))

    def send_game_results(self, winner):
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
