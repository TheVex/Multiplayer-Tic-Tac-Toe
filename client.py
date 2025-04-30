import pygame
import pygame_menu
from protocols.enums import Mark, WinLine, Response, Request
from pprint import pprint
import pygame_menu.themes
import socket
import json

# Board position customization
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 150
CELL_OFFSET = 20
LINE_WIDTH = 10
WIN_LINE_WIDTH = 15
# Position from which board starts drawing
START_POS =  (WIDTH // 2 - int(CELL_SIZE * 1.5), HEIGHT // 2 - int(CELL_SIZE * 1.5))

# Color customization
BACKGROUND_COLOR = 'lightgray'
BOARD_COLOR = 'black'
CROSS_COLOR = 'red'
CIRCLE_COLOR = 'blue'
WIN_LINE_COLOR = 'green'
SERVER_LIST_COLOR = (200, 200, 200)

FONT = None
FONT_SIZE = 64
TEXT_OFFSET = 30

SERVER_ADDRESS = ("127.0.0.1", 8080)
BUFFER_SIZE = 8192

pygame.init()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(5)
client_socket.setblocking(0)
pygame.display.set_caption("Tic-Tac-Toe")   
screen = pygame.display.set_mode((WIDTH, HEIGHT))


def send_request(request_type, data=None):
    try:
        request = {"type": request_type.value}
        if data:
            request.update(data)
        print("Doing")
        for key, value in request.items():
            print(f"Key: {key}, Value: {value}")
        client_socket.send(json.dumps(request).encode('utf-8'))
        response = json.loads(client_socket.recv(BUFFER_SIZE).decode('utf-8'))
        return response
    except Exception as e:
        print(f"Network error: {e}")
        return None


class Renderer:
    def __init__(self, screen):
        # Fill the screen with background color
        pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, WIDTH, HEIGHT))
        self.screen = screen
        
    # Draws cross on the screen
    def draw_cross(self, x, y) -> None:
        pygame.draw.line(self.screen, CROSS_COLOR,
                            (START_POS[0] + x * CELL_SIZE + CELL_OFFSET,
                             START_POS[1] + y * CELL_SIZE + CELL_OFFSET),
                            (START_POS[0] + (x + 1) * CELL_SIZE - CELL_OFFSET,
                             START_POS[1] + (y + 1) * CELL_SIZE - CELL_OFFSET),
                            LINE_WIDTH)
        pygame.draw.line(self.screen, CROSS_COLOR,
                            (START_POS[0] + (x + 1) * CELL_SIZE - CELL_OFFSET,
                             START_POS[1] + y * CELL_SIZE + CELL_OFFSET),
                            (START_POS[0] + x * CELL_SIZE + CELL_OFFSET,
                             START_POS[1] + (y + 1) * CELL_SIZE - CELL_OFFSET),
                            LINE_WIDTH)
    
    # Draws circle on the screen
    def draw_circle(self, x, y):
            pygame.draw.circle(self.screen, CIRCLE_COLOR,
                               (START_POS[0] + int((x + 0.5) * CELL_SIZE),
                                START_POS[1] + int((y + 0.5) * CELL_SIZE)),
                               CELL_SIZE // 2 - CELL_OFFSET, LINE_WIDTH)
    
    # Draw line showing the winner, handled by draw_winner() function
    def draw_winline(self, game):
        if game.winline == WinLine.HORIZONTAL:
            pygame.draw.line(self.screen, WIN_LINE_COLOR,
                            (START_POS[0], START_POS[1] + int((game.line + 0.5) * CELL_SIZE)),
                            (START_POS[0] + 3 * CELL_SIZE, START_POS[1] + int((game.line + 0.5) * CELL_SIZE)),
                            WIN_LINE_WIDTH)
        elif game.winline == WinLine.VERTICAL:
            pygame.draw.line(self.screen, WIN_LINE_COLOR,
                            (START_POS[0] + int((game.line + 0.5) * CELL_SIZE), START_POS[1]),
                            (START_POS[0] + int((game.line + 0.5) * CELL_SIZE), START_POS[1] + 3 * CELL_SIZE),
                            WIN_LINE_WIDTH)
        elif game.winline == WinLine.LEFT_DIAGONAL:
            pygame.draw.line(self.screen, WIN_LINE_COLOR, START_POS,
                            (START_POS[0] + 3 * CELL_SIZE, START_POS[1] + 3 * CELL_SIZE),
                            WIN_LINE_WIDTH)
        elif game.winline == WinLine.RIGHT_DIAGONAL:
            pygame.draw.line(self.screen, WIN_LINE_COLOR, 
                            (START_POS[0] + 3 * CELL_SIZE, START_POS[1]),
                            (START_POS[0], START_POS[1] + 3 * CELL_SIZE),
                            WIN_LINE_WIDTH)
    
    # Write game result, handled by render() function
    def draw_winner(self, game):
        self.draw_winline(game)
        text = None
        if game.winner == Mark.CROSS:
            text = FONT.render("Cross wins!", 0, 'black')
        elif game.winner == Mark.CIRCLE:
            text = FONT.render("Circle wins!", 0, 'black')
        elif game.winner == Mark.DRAW:
            text = FONT.render("Draw!", 0, 'black')

        text_rect = text.get_rect(center=(WIDTH/2, START_POS[1] + 3 * CELL_SIZE + TEXT_OFFSET))
        self.screen.blit(text, text_rect)
    
    # Draws the board
    def render(self, game) -> None:
        for i in range(1, 3):
            pygame.draw.line(self.screen, BOARD_COLOR, 
                           (START_POS[0] + i * CELL_SIZE, START_POS[1]),
                           (START_POS[0] + i * CELL_SIZE, START_POS[1] + 3 * CELL_SIZE),
                           LINE_WIDTH)
            pygame.draw.line(self.screen, BOARD_COLOR, 
                           (START_POS[0], START_POS[1] + i * CELL_SIZE),
                           (START_POS[0] + 3 * CELL_SIZE, START_POS[1] + i * CELL_SIZE),
                           LINE_WIDTH)

        for x in range(3):
            for y in range(3):
                if game.board[x][y] == Mark.CROSS:
                    self.draw_cross(y, x)
                elif game.board[x][y] == Mark.CIRCLE:
                    self.draw_circle(y, x)
                    
        if game.winline != WinLine.NOT_FINISHED:
            self.draw_winner(game)

    
class Game:
    def __init__(self, player_mark):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.my_mark = player_mark  
        self.current_turn = None 
        self.is_finished = False
        self.winner = Mark.NOT_FINISHED
        self.winline = WinLine.NOT_FINISHED
        self.turn = Mark.CROSS

    def update_from_server(self, board, current_turn, is_finished):
        self.board = board
        self.current_turn = current_turn
        self.is_finished = is_finished
            
    # Checks that mouse cursor is in board and places mark
    def set_local_mark(self, mark):
        if self.is_finished:
            print("Game already finished.")
            return False
        if self.current_turn != self.my_mark:
            print("Not your turn.")
            return False
        x_mouse, y_mouse = pygame.mouse.get_pos()
        for x in range(3):
            for y in range(3):
                if (self.board[x][y] is None and
                    START_POS[0] + y * CELL_SIZE < x_mouse < START_POS[0] + (y + 1) * CELL_SIZE and
                    START_POS[1] + x * CELL_SIZE < y_mouse < START_POS[1] + (x + 1) * CELL_SIZE):
                    return x, y
        print("Invalid cell.")
        return False
        
    # Hardcoded conditions check
    def check_game_end(self):
        pprint(self.board)
        
        for i in range(3):
            if self.board[i][0] and self.board[i][0] == self.board[i][1] == self.board[i][2]:
                return self.set_win_condition(i, self.board[i][0], WinLine.HORIZONTAL)
            if self.board[0][i] and self.board[0][i] == self.board[1][i] == self.board[2][i]:
                return self.set_win_condition(i, self.board[0][i], WinLine.VERTICAL)
    
        if self.board[0][0] and self.board[0][0] == self.board[1][1] == self.board[2][2]:
            return self.set_win_condition(0, self.board[0][0], WinLine.LEFT_DIAGONAL)
        if self.board[0][2] and self.board[0][2] == self.board[1][1] == self.board[2][0]:
            return self.set_win_condition(0, self.board[0][2], WinLine.RIGHT_DIAGONAL)
        
        if all(cell is not None for row in self.board for cell in row):
            return self.set_win_condition(0, Mark.DRAW, WinLine.DRAW)
        
        return False

    def set_win_condition(self, line, winner, winline):
        self.line = line
        self.winner = winner
        self.winline = winline
        return True
     
                
def initialize_screen(screen):
    renderer = Renderer(screen)
    # Create game
    game = Game()
    renderer.render(game)
    return renderer, game, Mark.CROSS, False, False, False


def convert_board(board):
    conv = [[None for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            if board[i][j] is not None:
                conv[i][j] = Mark(board[i][j])
    return conv

    
def start_game(game_id=None, is_host=False):
    global FONT, screen
 
    if game_id is not None:
        if is_host:
            response = send_request(Request.CREATE_THE_GAME)
            if response and response.get("type") == Response.CREATE_GAME.value:
                game_id = response["data"][0]
                player_id = response["data"][1]
                player_mark = Mark.CROSS
                show_waiting_screen(game_id)
            else:
                print("Failed to create game")
                return
        else:
            response = send_request(Request.CONNECT_TO_GAME, {"game_id": game_id})
            if response and response.get("type") == Response.CONNECT_TO_GAME.value:
                player_id = response["data"]
                player_mark = Mark.CIRCLE
            else:
                print("Failed to join game")
                return
            
    FONT = pygame.font.Font(None, FONT_SIZE)
    renderer = Renderer(screen)
    game = Game(player_mark)
    renderer.render(game)


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
 
            if event.type == pygame.MOUSEBUTTONDOWN and game.winner == Mark.NOT_FINISHED:
                x_mouse, y_mouse = pygame.mouse.get_pos()
                for x in range(3):
                    for y in range(3):
                        if (game.board[x][y] is None and
                            START_POS[0] + y * CELL_SIZE < x_mouse < START_POS[0] + (y + 1) * CELL_SIZE and
                            START_POS[1] + x * CELL_SIZE < y_mouse < START_POS[1] + (x + 1) * CELL_SIZE):

                            if game.turn == player_mark:
                                response = send_request(Request.MAKE_THE_MOVE, {
                                    "game_id": game_id,
                                    "client_id": player_id,
                                    "row": x,
                                    "col": y
                                })
                                if response and response.get("type") == Response.MOVE_MADE.value:
                                    game.board = convert_board(response["board"])
                                    game.turn = Mark(response["turn"])
                                elif response and response.get("type") == Response.GAME_FINISHED_SUC.value:
                                    game.board = convert_board(response["board"])
                                    game.winner = Mark(response["winner"])
 
        if game_id is not None and game.winner == Mark.NOT_FINISHED:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if data:
                    response = json.loads(data.decode('utf-8'))
                    if response["type"] == Response.MOVE_MADE.value:
                        game.board = convert_board(response["board"])
                        game.turn = Mark(response["turn"])
                    elif response["type"] == Response.GAME_FINISHED_SUC.value:
                        game.board = convert_board(response["board"])
                        game.winner = Mark(response["winner"])
                    elif response["type"] == Response.PLAYER_DISCONNECTED.value:
                        print("Opponent disconnected... Waiting it to reconnect")
                    elif response["type"] == Response.GAME_FINISHED_TECH.value:
                        game.board = convert_board(response["board"])
                        game.winner = Mark(game.turn)
                        print("Opponent failed to connect.")
            except BlockingIOError:
                pass
            except TimeoutError:
                print("Waiting for another host to make a move.")
 
        renderer.render(game)
        pygame.display.flip()
 
    if game_id is not None:
        client_socket.close()

# Waiting screen 
def show_waiting_screen(game_id):
    waiting = True
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
 
    screen.fill(BACKGROUND_COLOR)
    text = font.render("Waiting for opponent...", True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
    screen.blit(text, text_rect)
    pygame.display.flip()

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
 
        try:
            data = client_socket.recv(BUFFER_SIZE)
            if data:
                response = json.loads(data.decode('utf-8'))
                if response["type"] == Response.START_GAME.value:
                    waiting = False
        except BlockingIOError:
            pass
        except TimeoutError:
            print("Waiting for game to start...")
 
        screen.fill(BACKGROUND_COLOR)
        text = font.render("Waiting for opponent...", True, (0, 0, 0))
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.blit(text, text_rect)
 
        pygame.display.flip()
        clock.tick(30)
        

def lobby(page=0): 
    response = send_request(Request.GET_GAMES, {
        "page_num_l": page * 8,
        "page_num_r": (page + 1) * 8 - 1
    })
 
    if not response or response.get("type") != Response.RETURN_GAMES.value:
        print("Failed to get game list")
        return
 
    available_games = response["data"]
    total_pages = (len(available_games) + 7) // 8
 
    lobby_menu = pygame_menu.Menu("Lobby", WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_SOLARIZED)
 
    controls_frame = lobby_menu.add.frame_h(width=WIDTH*0.8, height=50)
 
    page_info_label = controls_frame.pack(
        lobby_menu.add.label(f"Page {page+1}/{total_pages}", font_size=20),
        align=pygame_menu.locals.ALIGN_CENTER
    )
 
    content_frame = lobby_menu.add.frame_v(
        width=WIDTH*0.8,
        height=HEIGHT*0.5,
        background_color=SERVER_LIST_COLOR
    )
 
    for game_id in available_games:
        content_frame.pack(
            lobby_menu.add.button(
                f"Game {game_id+1}", 
                lambda g=game_id: start_game(g),
                font_size=20
            ),
            align=pygame_menu.locals.ALIGN_CENTER
        )
 
    def change_page(delta):
        nonlocal page
        new_page = page + delta
        if 0 <= new_page < total_pages:
            lobby_menu.close()
            lobby(new_page)
 
    btn_prev = controls_frame.pack(
        lobby_menu.add.button(
            "<", 
            lambda: change_page(-1),
            font_size=20
        ),
        align=pygame_menu.locals.ALIGN_LEFT
    )
 
    btn_next = controls_frame.pack(
        lobby_menu.add.button(
            ">", 
            lambda: change_page(1),
            font_size=20
        ),
        align=pygame_menu.locals.ALIGN_RIGHT
    )
 
    lobby_menu.add.button("Create Game", lambda: start_game(game_id=-1, is_host=True), font_size=20)
    lobby_menu.add.button("Refresh", lambda: lobby(page), font_size=20)
    lobby_menu.add.button("Back", pygame_menu.events.BACK, font_size=20)
 
    lobby_menu.mainloop(screen)
    
      
def menu():
    menu = pygame_menu.Menu("Tic-Tac-Toe", WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_SOLARIZED)
    menu.add.button('Play', lobby)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    menu.mainloop(screen)
    
if __name__ == '__main__':
    try:
        client_socket.connect(SERVER_ADDRESS)
    except Exception as e:
        print(f"Failed to connect to server: {e}")
    menu()