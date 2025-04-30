import socket
import json
from protocols.enums import Request, Response, Mark


SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080
BUFFER_SIZE = 4096

class GameClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SERVER_IP, SERVER_PORT))
        self.client_id = None

    def get_games(self, page_num_l, page_num_r):
        request = dict()
        request["type"] = Request.GET_GAMES
        request["page_num_l"] = page_num_l
        request["page_num_r"] = page_num_r
        json_request = json.dumps(request).encode("utf-8")  
        self.sock.send(json_request)

        response = json.loads(self.sock.recv(BUFFER_SIZE).decode('utf-8'))
        data = None
        if response["type"] == Response.ERROR:
            # Raise an error and process it
            pass
        else:
            data = response["data"]
        return data
    
    def create_the_game(self):
        request = dict()
        request["type"] = Request.CREATE_THE_GAME
        json_request = json.dumps(request).encode("utf-8")  
        self.sock.send(json_request)

        response = json.loads(self.sock.recv(BUFFER_SIZE).decode('utf-8'))
        data = None
        if response["type"] == Response.ERROR:
            # Raise an error and process it
            pass
        else:
            data = response["data"]
        self.client_id = data["client_id"]
        return data
    
    def connect_to_game(self, game_id):
        request = dict()
        request["type"] = Request.CONNECT_TO_GAME
        request["game_id"] = game_id
        json_request = json.dumps(request).encode("utf-8")  
        self.sock.send(json_request)

        response = json.loads(self.sock.recv(BUFFER_SIZE).decode('utf-8'))
        if response["type"] == Response.ERROR:
            # Raise an error and process it
            pass
        else:
            player_id = response["data"]
        return player_id
    
    def make_the_move(self, row, col):
        request = dict()
        request["type"] = Request.MAKE_THE_MOVE
        request["client_id"] = self.client_id
        request["row"] = row
        request["col"] = col
        json_request = json.dumps(request).encode("utf-8")  
        self.sock.send(json_request)

        response = json.loads(self.sock.recv(BUFFER_SIZE).decode('utf-8'))
        if response["type"] == Response.ERROR:
            # Raise an error and process it
            pass
        elif response["type"] == Response.GAME_FINISHED_SUC:
            pass
        elif response["type"] == Request.