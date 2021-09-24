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

    BOARD_DIMENSION = 3

    def __init__(self, player_1, player_2):
        if (not isinstance(player_1, Player)) or (not isinstance(player_2, Player)) or (player_1 == player_2):
            raise ValueError('Invalid players provided!')

        self.player_1 = player_1
        self.player_2 = player_2
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
                        raise ValueError('Board should be updated at a single empty cell!')
                    number_of_changes += 1
                    changed_cell = (row_index, column_index)
        
        if number_of_changes != 1:
            raise ValueError('Board should be updated at a single empty cell!')
        
        return changed_cell

    def validate_player(self, player):
        if (not self.player_1) or (not self.player_2):
            raise ValueError('Players are missing!')

        if (player != self.player_1) and (player != self.player_2):
            raise ValueError('Unknown player provided!')

    def process(self, player, updated_board):
        self.validate_player(player)
        updated_row, updated_column = self.validate_board(updated_board)
        self.board[updated_row][updated_column] = self.get_value_from_player(player)

    def is_won(self):
        for scenario in self.WIN_MAP:
            value_1 = self.board[scenario[0][0]][scenario[0][1]]
            value_2 = self.board[scenario[1][0]][scenario[1][1]]
            value_3 = self.board[scenario[2][0]][scenario[2][1]]
            if value_1 == value_2 == value_3 != ' ':
                return self.get_player_from_value(value_1)
        return False

    def get_value_from_player(self, player):
        self.validate_player(player)

        if player == self.player_1:
            return 'X'
        return 'O'

    def get_player_from_value(self, value):
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
        print(f'Listening for incoming connection on port {self.PORT}')

        while len(self.clients) < 2:
            connection, address = self.socket.accept()
            self.clients.append(Client(f'Player {len(self.clients) + 1}', connection, address))
            print(f'Connected by {address}')

        print(f'{len(self.clients)} clients are now connected')
        print('Starting the game')
        self.play_game()
        self.socket.close()

    def change_turn(self):
        if self.turn == 0:
            self.turn = 1
        else:
            self.turn = 0

    def get_current_player(self) -> Client:
        return self.clients[self.turn]

    def get_player_move(self, player, data):
        connection = player.connection
        connection.sendall(bytes(data, 'utf-8'))

        input = connection.recv(1024)
        if not input:
            return None

        print(f'{player.name} sent this message:')
        print(input)
        return json.loads(input)

    def play_game(self):
        game = Game(self.clients[0], self.clients[1])
        winner = None

        while True:
            player = self.get_current_player()
            board = json.dumps(game.get_board_copy())
            updated_board = self.get_player_move(player, board)
            print(updated_board)
            try:
                game.process(player, updated_board)
            except Exception as e:
                print(e)
                continue
            winner = game.is_won()
            if winner:
                break
            self.change_turn()
        
        if winner:
            print(f'{winner.name} Won!')
        else:
            print('It is a tie')
