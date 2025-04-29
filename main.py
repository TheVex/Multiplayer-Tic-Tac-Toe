import pygame
import pygame_menu
from enum import Enum
from pprint import pprint

import pygame_menu.themes

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

pygame.init()
pygame.display.set_caption("Tic-Tac-Toe")   
screen = pygame.display.set_mode((WIDTH, HEIGHT))


# Specifies type of mark (and who won the game)
class Mark(Enum):
    NOT_FINISHED = 4
    CROSS = 1
    CIRCLE = 2
    DRAW = 3
    
# Specifies type of line showing the winner
class WinLine(Enum):
    NOT_FINISHED = 6
    HORIZONTAL = 1
    VERTICAL = 2
    LEFT_DIAGONAL = 3
    RIGHT_DIAGONAL = 4
    DRAW = 5


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
    def __init__(self):
        self.board = [[None for _ in range(3)] for i in range(3)]
        self.winline = WinLine.NOT_FINISHED
        self.line = -1
        self.winner = Mark.NOT_FINISHED
            
    # Checks that mouse cursor is in board and places mark
    def set_mark(self, mark) -> bool:
        x_mouse, y_mouse = pygame.mouse.get_pos()
        for x in range(3):
            for y in range(3):
                if (self.board[x][y] is None and
                    START_POS[0] + y * CELL_SIZE < x_mouse < START_POS[0] + (y + 1) * CELL_SIZE and
                    START_POS[1] + x * CELL_SIZE < y_mouse < START_POS[1] + (x + 1) * CELL_SIZE):
                    self.board[x][y] = mark
                    return True
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
    
    
# I think should be partially moved to the server
def start_game():
    global FONT, screen
    # Create game window
    
    FONT = pygame.font.Font(None, FONT_SIZE)
    '''
    "renderer" draws game on the screen
    "game" is a class instance with all logic
    "turn" Defines which player turn is
    "end" checks if game is finished
    "mark_success" checks if mark placed on board correctly
    "restart" checks if players want to restart the game
    '''
    renderer, game, turn, end, mark_success, restart = initialize_screen(screen)
    
    # If game continues
    running = True
    while running:
        if restart:
            renderer, game, turn, end, mark_success, restart = initialize_screen(screen)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not end and event.type == pygame.MOUSEBUTTONDOWN:
                mark_success = game.set_mark(turn)
            if end and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                restart = True
                
        if end:
            pass
        else:
            if mark_success:
                if turn == Mark.CIRCLE:
                    turn = Mark.CROSS
                else:
                    turn = Mark.CIRCLE
                mark_success = False
                end = game.check_game_end()
        renderer.render(game)
        pygame.display.flip()
    
    pygame.quit()


# Thank you DeepSeek for lobby generation!
def lobby(page=0):
    # Имитация данных (в реальном приложении получаем с сервера)
    TOTAL_SESSIONS = 12
    SESSIONS_PER_PAGE = 10
    
    current_page = page
    total_pages = (TOTAL_SESSIONS + SESSIONS_PER_PAGE - 1) // SESSIONS_PER_PAGE
    
    lobby_menu = pygame_menu.Menu("Lobby", WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_SOLARIZED)
    
    # Элементы управления
    controls_frame = lobby_menu.add.frame_h(width=WIDTH*0.8, height=50)
    
    # Информация о странице
    page_info_label = controls_frame.pack(
        lobby_menu.add.label(f"Page {current_page+1}/{total_pages}", font_size=20),
        align=pygame_menu.locals.ALIGN_CENTER
    )
    
    # Контейнер для динамического контента
    content_frame = lobby_menu.add.frame_v(
        width=WIDTH*0.8,
        height=HEIGHT*0.7,
        background_color=SERVER_LIST_COLOR
    )

    # Рассчитываем диапазон сессий для текущей страницы
    start_idx = current_page * SESSIONS_PER_PAGE
    end_idx = min(start_idx + SESSIONS_PER_PAGE, TOTAL_SESSIONS)
        
    # Добавляем кнопки сессий
    for i in range(start_idx, end_idx):
        content_frame.pack(
            lobby_menu.add.button(
                f"Game {i+1}", 
                start_game,
                font_size=20
            ),
            align=pygame_menu.locals.ALIGN_CENTER
        )
    
    # Функция смены страницы
    def change_page(delta):
        nonlocal current_page
        new_page = current_page + delta
        
        if 0 <= new_page < total_pages:
            # Создаем новое меню с новой страницей
            lobby_menu.close()
            lobby(new_page)
    
    # Кнопка назад
    btn_prev = controls_frame.pack(
        lobby_menu.add.button(
            "<", 
            lambda: change_page(-1),
            font_size=20
        ),
        align=pygame_menu.locals.ALIGN_LEFT
    )
    
    # Кнопка вперед
    btn_next = controls_frame.pack(
        lobby_menu.add.button(
            ">", 
            lambda: change_page(1),
            font_size=20
        ),
        align=pygame_menu.locals.ALIGN_RIGHT
    )
    
    # Кнопка обновления (теперь просто пересоздает текущую страницу)
    lobby_menu.add.button("Refresh", lambda: lobby(current_page), font_size=20)
    lobby_menu.add.button("Back", pygame_menu.events.BACK, font_size=20)
    
    lobby_menu.mainloop(screen)
    
      
def menu():
    menu = pygame_menu.Menu("Tic-Tac-Toe", WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_SOLARIZED)
    menu.add.button('Play', lobby)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    menu.mainloop(screen)
    
if __name__ == '__main__':
    menu()