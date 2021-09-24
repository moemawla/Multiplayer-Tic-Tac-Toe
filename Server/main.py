from classes import *

#server = Server()
#server.run()
player_1 = Player(1)
player_2 = Player(2)
game = Game(player_1, player_2)
turns = [
    [
        ['X', ' ', ' '],
        [' ', ' ', ' '],
        [' ', ' ', ' ']
    ],
    [
        ['X', 'O', ' '],
        [' ', ' ', ' '],
        [' ', ' ', ' ']
    ],
    [
        ['X', 'O', ' '],
        [' ', 'X', ' '],
        [' ', ' ', ' ']
    ],
    [
        ['X', 'O', 'O'],
        [' ', 'X', ' '],
        [' ', ' ', ' ']
    ],
    [
        ['X', 'O', 'O'],
        [' ', 'X', ' '],
        [' ', ' ', 'X']
    ],
]

player = player_2
winner = None

for board in turns:
    if player == player_1:
        player = player_2
    else:
        player = player_1
    
    game.process(player, board)
    winner = game.is_won()
    if winner:
        break

if winner:
    print(f'player # {winner.id} Won!!')
else:
    print('It is a tie')
