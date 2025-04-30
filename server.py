import socket
from threading import Thread, Timer
from protocols.enums import Request, Response, Mark
from log_meth import log
import json
import random


IP = "127.0.0.1"
PORT = 8080
SERVER_BUFFER = 8192


class Client:
    def __init__(self, host_sock, host_addr, banned_id=[]):
        self.host_sock = host_sock
        self.host_addr = host_addr
        self.host_id = self.create_identifier(banned_id)

    def create_identifier(self, banned=[]):
        banned_set = set(banned)
        id = random.randint(10000, 99999)
        while id in banned_set:
            id = random.randint(10000, 99999)
        return id
    
    def verify(self, host_sock, host_addr, host_id):
        if self.host_addr != host_addr and self.host_id != host_id:
            return False
        elif self.host_addr != host_addr and self.host_id == host_id:
            self.host_addr = host_addr
            self.host_sock = host_sock
            return True
        return True


class Game:
    def __init__(self, game_id):
        self.clients = [None, None]
        self.connected = 0
        self.game_id = game_id
        self.finished = False
        self.turn = Mark.CROSS
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.disconnect_timer = [None, None]

    def connect_client(self, host_sock, host_addr):
        res = None
        if self.connected < 2:
            banned = []
            if self.connected == 1:
                banned.append(self.clients[0].host_id)
            self.clients[self.connected] = Client(host_sock, host_addr, banned)
            res = self.clients[self.connected].host_id
            self.connected += 1
        return res
    
    def check_winner(self, board):
        lines = []
        lines.extend(board)
        lines.extend([[board[r][c] for r in range(3)] for c in range(3)])
        lines.append([board[i][i] for i in range(3)])
        lines.append([board[i][2 - i] for i in range(3)])
        for line in lines:
            if line[0] is not None and all(cell == line[0] for cell in line):
                return line[0]
        if all(cell is not None for row in board for cell in row):
            return Mark.DRAW
        return None

    def change_turn(self):
        self.turn = Mark.CIRCLE if self.turn == Mark.CROSS else Mark.CROSS


class GameServer:
    def __init__(self, sock, addr):
        self.games = []
        self.games_count = 0
        self.sock = sock
        self.addr = addr

    def create_game(self):
        game_id = self.games_count
        self.games_count += 1
        game = Game(game_id)
        self.games.append(game)
        log.log_info(f"Created new game with ID {game_id}")
        return game
    
    def disconnect_timeout(self, game, index):
        if game.disconnected[index]:
            game.finished = True
            other_index = 1 - index
            winner = None
            if game.clients[other_index]:
                 winner = game.clients[other_index].host_id
            log.log_info(f"Client {game.clients[index].host_id} failed to reconnect. Game {game.game_id} ended. Winner: {winner}")
            if game.clients[other_index]:
                try:
                    game.clients[other_index].host_sock.send(json.dumps({
                        "type": Response.GAME_FINISHED_TECH.value,
                        "winner": winner,
                        "board": game.board,
                    }).encode("utf-8"))
                except Exception as e:
                    log.log_warn(f"Failed to notify player {winner} after timeout: {e}")

    def serve_connection(self, client_sock, client_addr):
        log.log_info(f"New client connected: {client_addr}")
        while True:
            try:
                message = client_sock.recv(SERVER_BUFFER)
                log.log_info(f"Message was received from client: {client_addr}")
                data = json.loads(message.decode('utf-8'))
                response = dict()

                if int(data['type']) == Request.GET_GAMES.value:
                    page_num_l = int(data["page_num_l"])
                    page_num_r = int(data["page_num_r"])
                    if page_num_l < 0 or page_num_l > self.games_count or page_num_r < 0:
                        raise IndexError("Invalid page range: left or right index out of bounds")
                    response["type"] = Response.RETURN_GAMES.value
                    response["data"] = [i for i in range(page_num_l, min(page_num_r, self.games_count))]
                    json_response = json.dumps(response).encode("utf-8")
                    client_sock.send(json_response)
                    
                elif int(data['type']) == Request.CONNECT_TO_GAME.value:
                    game_id = data['game_id']
                    if game_id < 0 or game_id >= self.games_count:
                        raise IndexError(f"Game ID {game_id} does not exist")
                    if self.games[game_id].connected >= 2:
                        raise RuntimeError(f"Game {game_id} is already full")
                    res = self.games[game_id].connect_client(client_sock, client_addr)
                    if res is None:
                        raise RuntimeError(f"Failed to connect client to game {game_id}")
                    log.log_info(f"Client {client_addr} connected to game {game_id}")
                    creator = self.games[game_id].clients[0].host_sock
                    creator_response = {"type": Response.START_GAME.value}
                    creator.send(json.dumps(creator_response).encode("utf-8"))
                    response["type"] = Response.CONNECT_TO_GAME.value
                    response["data"] = res
                    client_sock.send(json.dumps(response).encode("utf-8"))

                elif int(data["type"]) == Request.RECONNECT_CLIENT.value:
                    host_id = data["host_id"]
                    for game in self.games:
                        for i, client in enumerate(game.clients):
                            if client and client.host_id == host_id:
                                if not game.disconnected[i]:
                                    raise RuntimeError("Client already connected.")
                                client.host_sock = client_sock
                                client.host_addr = client_addr
                                game.disconnected[i] = False
                                if game.disconnect_timer[i]:
                                    game.disconnect_timer[i].cancel()
                                response["type"] = Response.RECONNECTED.value
                                response["game_id"] = game.game_id
                                response["board"] = game.board
                                response["your_mark"] = Mark.CROSS if i == 0 else Mark.CIRCLE
                                response["turn"] = game.turn
                                client_sock.send(json.dumps(response).encode("utf-8"))
                                log.log_info(f"Client {host_id} reconnected to game {game.game_id}")
                                break

                elif int(data["type"]) == Request.CREATE_THE_GAME.value:
                    game = self.create_game()
                    client_id = game.connect_client(client_sock, client_addr)
                    response["type"] = Response.CREATE_GAME.value
                    response["data"] = [game.game_id, client_id]
                    client_sock.send(json.dumps(response).encode("utf-8"))

                elif int(data["type"]) == Request.MAKE_THE_MOVE.value:
                    game_id = data['game_id']
                    client_id = data['client_id']
                    row = data['row']
                    col = data['col']
                    if game_id < 0 or game_id >= self.games_count:
                        raise IndexError(f"Game ID {game_id} does not exist")
                    game = self.games[game_id]
                    if not any(client and client.host_id == client_id for client in game.clients):
                        raise ValueError(f"Invalid client ID {client_id} for game {game_id}")
                    player_index = 1
                    if game.clients[0].host_id == client_id:
                        player_index = 0
                    player_mark = Mark.CIRCLE if player_index == 1 else Mark.CROSS
                    if game.turn != player_mark:
                        raise ValueError("Not your turn")
                    if not (0 <= row < 3 and 0 <= col < 3):
                        raise ValueError("Invalid move position")
                    if game.board[row][col] is not None:
                        raise ValueError("Cell already taken")
                    game.board[row][col] = player_mark
                    log.log_info(f"Player {client_id} made move at ({row}, {col}) in game {game_id}")
                    winner = game.check_winner(game.board)
                    if winner:
                        game.finished = True
                        log.log_info(f"Game {game_id} finished. Winner: {winner.name}")
                        for client in game.clients:
                            win_resp = {
                                "type": Response.GAME_FINISHED_SUC.value,
                                "winner": winner,
                                "board": game.board
                            }
                            client.host_sock.send(json.dumps(win_resp).encode("utf-8"))
                        break
                    game.change_turn()
                    for client in game.clients:
                        move_resp = {
                            "type": Response.MOVE_MADE.value,
                            "board": game.board,
                            "turn": game.turn
                        }
                        client.host_sock.send(json.dumps(move_resp).encode("utf-8"))

            except (ConnectionResetError, BrokenPipeError):
                log.log_warn(f"Client {client_addr} disconnected.")
                for game in self.games:
                    if game.finished:
                        continue
                    for i, client in enumerate(game.clients):
                        if client and client.host_addr == client_addr:
                            game.disconnected[i] = True
                            log.log_warn(f"Client {client.host_id} disconnected. Waiting 30s for reconnection.")
                            game.disconnect_timer[i] = Timer(30.0, self.disconnect_timeout, args=(game, i))
                            game.disconnect_timer[i].start()
                            other_index = 1 - i
                            if game.clients[other_index]:
                                try:
                                    game.clients[other_index].host_sock.send(json.dumps({
                                        "type": Response.PLAYER_DISCONNECTED.value,
                                        "game_id": game.game_id
                                    }).encode("utf-8"))
                                    log.log_info(f"Notified player {game.clients[other_index].host_id} about opponent disconnection.")
                                except Exception as e:
                                    log.log_warn(f"Failed to notify player {game.clients[other_index].host_id} about opponent disconnection: {e}")
                            break
                break

            except Exception as e:
                log.log_error(f"Error handling client {client_addr}: {e}")
                error_resp = {
                    "type": Response.ERROR.value,
                    "data": str(e)
                }
                client_sock.send(json.dumps(error_resp).encode("utf-8"))


def start_server():
    server_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server_addr = (IP, PORT)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(server_addr)
    server_sock.listen(16)
    server_sock.settimeout(5)
    server = GameServer(server_sock, server_addr)
    log.log_info(f"Server started on {server_addr[0]}:{server_addr[1]}")
    try:
        while True:
            try:
                client_sock, client_addr = server_sock.accept()
                thread = Thread(target=server.serve_connection, args=(client_sock, client_addr))
                thread.daemon = True
                thread.start()
            except TimeoutError:
                log.log_info("No clients requesting for connection.")
    except KeyboardInterrupt:
        log.log_info("Server shutdown requested by user.")
    finally:
        server_sock.close()
        log.log_info("Server socket closed.")


if __name__ == "__main__":
    start_server()
