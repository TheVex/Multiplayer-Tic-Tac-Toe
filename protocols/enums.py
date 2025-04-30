from enum import Enum

# Specifies type of mark (and who won the game)
class Mark(Enum): 
    CROSS = 1
    CIRCLE = 2
    DRAW = 3
    NOT_FINISHED = 4
    
# Specifies type of line showing the winner
class WinLine(Enum):
    NOT_FINISHED = 6
    HORIZONTAL = 1
    VERTICAL = 2
    LEFT_DIAGONAL = 3
    RIGHT_DIAGONAL = 4
    DRAW = 5

# Specifies types of requests
class Request(Enum):
    GET_GAMES = 1
    CREATE_THE_GAME = 2
    CONNECT_TO_GAME = 3
    MAKE_THE_MOVE = 4
    RECONNECT_CLIENT = 5
    REMOVE_THE_GAME = 6

# Specifies types of responses
class Response(Enum):
    RETURN_GAMES = 1
    CREATE_GAME = 2
    CONNECT_TO_GAME = 3
    START_GAME = 4
    GAME_FINISHED_SUC = 5
    GAME_FINISHED_TECH = 6
    MOVE_MADE = 7
    ERROR = 8
    PLAYER_DISCONNECTED = 9
    RECONNECTED = 10