import pygame
from enum import Enum
from pprint import pprint

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 150
CELL_OFFSET = 20
LINE_WIDTH = 10
WIN_LINE_WIDTH = 15

BACKGROUND_COLOR = 'lightgray'
BOARD_COLOR = 'black'
CROSS_COLOR = 'red'
CIRCLE_COLOR = 'blue'
WIN_LINE_COLOR = 'green'

FONT = None
FONT_SIZE = 64
TEXT_OFFSET = 30

class Mark(Enum):
    NOT_FINISHED = 4
    CROSS = 1
    CIRCLE = 2
    DRAW = 3
    
    
class WinLine(Enum):
    NOT_FINISHED = 6
    HORIZONTAL = 1
    VERTICAL = 2
    LEFT_DIAGONAL = 3
    RIGHT_DIAGONAL = 4
    DRAW = 5

    
class Board:
    def __init__(self, screen):
        self.board = [[None for _ in range(3)] for i in range(3)]
        self.start_pos = (WIDTH // 2 - int(CELL_SIZE * 1.5),
                          HEIGHT // 2 - int(CELL_SIZE * 1.5))
        self.screen = screen
        self.winline = WinLine.NOT_FINISHED
        self.line = -1
        self.winner = Mark.NOT_FINISHED
          
    
    def draw_cross(self, x, y) -> None:
        pygame.draw.line(self.screen, CROSS_COLOR,
                            (self.start_pos[0] + x * CELL_SIZE + CELL_OFFSET,
                             self.start_pos[1] + y * CELL_SIZE + CELL_OFFSET),
                            (self.start_pos[0] + (x + 1) * CELL_SIZE - CELL_OFFSET,
                             self.start_pos[1] + (y + 1) * CELL_SIZE - CELL_OFFSET),
                            LINE_WIDTH)
        pygame.draw.line(self.screen, CROSS_COLOR,
                            (self.start_pos[0] + (x + 1) * CELL_SIZE - CELL_OFFSET,
                             self.start_pos[1] + y * CELL_SIZE + CELL_OFFSET),
                            (self.start_pos[0] + x * CELL_SIZE + CELL_OFFSET,
                             self.start_pos[1] + (y + 1) * CELL_SIZE - CELL_OFFSET),
                            LINE_WIDTH)
        
        
    def draw_circle(self, x, y):
            pygame.draw.circle(self.screen, CIRCLE_COLOR,
                               (self.start_pos[0] + int((x + 0.5) * CELL_SIZE),
                                self.start_pos[1] + int((y + 0.5) * CELL_SIZE)),
                               CELL_SIZE // 2 - CELL_OFFSET, LINE_WIDTH)
            
    def draw_winline(self):
        if self.winline == WinLine.HORIZONTAL:
            pygame.draw.line(self.screen, WIN_LINE_COLOR,
                            (self.start_pos[0], self.start_pos[1] + int((self.line + 0.5) * CELL_SIZE)),
                            (self.start_pos[0] + 3 * CELL_SIZE, self.start_pos[1] + int((self.line + 0.5) * CELL_SIZE)),
                            WIN_LINE_WIDTH)
        elif self.winline == WinLine.VERTICAL:
            pygame.draw.line(self.screen, WIN_LINE_COLOR,
                            (self.start_pos[0] + int((self.line + 0.5) * CELL_SIZE), self.start_pos[1]),
                            (self.start_pos[0] + int((self.line + 0.5) * CELL_SIZE), self.start_pos[1] + 3 * CELL_SIZE),
                            WIN_LINE_WIDTH)
        elif self.winline == WinLine.LEFT_DIAGONAL:
            pygame.draw.line(self.screen, WIN_LINE_COLOR, self.start_pos,
                            (self.start_pos[0] + 3 * CELL_SIZE, self.start_pos[1] + 3 * CELL_SIZE),
                            WIN_LINE_WIDTH)
        elif self.winline == WinLine.RIGHT_DIAGONAL:
            pygame.draw.line(self.screen, WIN_LINE_COLOR, 
                            (self.start_pos[0] + 3 * CELL_SIZE, self.start_pos[1]),
                            (self.start_pos[0], self.start_pos[1] + 3 * CELL_SIZE),
                            WIN_LINE_WIDTH)
            
    def set_winner(self):
        self.draw_winline()
        text = None
        if self.winner == Mark.CROSS:
            text = FONT.render("Cross wins!", 0, 'black')
        elif self.winner == Mark.CIRCLE:
            text = FONT.render("Circle wins!", 0, 'black')
        elif self.winner == Mark.DRAW:
            text = FONT.render("Draw!", 0, 'black')

        text_rect = text.get_rect(center=(WIDTH/2, self.start_pos[1] + 3 * CELL_SIZE + TEXT_OFFSET))
        self.screen.blit(text, text_rect)
        
    def render(self) -> None:
        for i in range(1, 3):
            pygame.draw.line(self.screen, BOARD_COLOR, 
                           (self.start_pos[0] + i * CELL_SIZE, self.start_pos[1]),
                           (self.start_pos[0] + i * CELL_SIZE, self.start_pos[1] + 3 * CELL_SIZE),
                           LINE_WIDTH)
            pygame.draw.line(self.screen, BOARD_COLOR, 
                           (self.start_pos[0], self.start_pos[1] + i * CELL_SIZE),
                           (self.start_pos[0] + 3 * CELL_SIZE, self.start_pos[1] + i * CELL_SIZE),
                           LINE_WIDTH)

        for x in range(3):
            for y in range(3):
                if self.board[x][y] == Mark.CROSS:
                    self.draw_cross(y, x)
                elif self.board[x][y] == Mark.CIRCLE:
                    self.draw_circle(y, x)
                    
        if self.winline != WinLine.NOT_FINISHED:
            self.set_winner()
            
 
    def set_mark(self, mark) -> bool:
        x_mouse, y_mouse = pygame.mouse.get_pos()
        for x in range(3):
            for y in range(3):
                if (self.board[x][y] is None and
                    self.start_pos[0] + y * CELL_SIZE < x_mouse < self.start_pos[0] + (y + 1) * CELL_SIZE and
                    self.start_pos[1] + x * CELL_SIZE < y_mouse < self.start_pos[1] + (x + 1) * CELL_SIZE):
                    self.board[x][y] = mark
                    return True
        return False
    
    
        

        
        
    # Hardcoded conditions check
    def check_game_end(self):
        pprint(self.board)
        
        for i in range(3):
            if self.board[i][0] != None and self.board[i][0] == self.board[i][1] == self.board[i][2]:
                self.line, self.winner, self.winline = i, self.board[i][0], WinLine.HORIZONTAL
                return True
            elif self.board[0][i] != None and self.board[0][i] == self.board[1][i] == self.board[2][i]:
                self.line, self.winner, self.winline = i, self.board[0][i], WinLine.VERTICAL
                return True
            
        if self.board[0][0] is not None and self.board[0][0] == self.board[1][1] == self.board[2][2]:
            self.line, self.winner, self.winline = 0, self.board[0][0], WinLine.LEFT_DIAGONAL
            return True
        if self.board[0][2] is not None and self.board[0][2] == self.board[1][1] == self.board[2][0]:
            self.line, self.winner, self.winline = 0, self.board[0][2], WinLine.RIGHT_DIAGONAL
            return True
        
        draw = True
        for row in self.board:
            for cell in row:
                if cell == None:
                    draw = False
        if draw:
            self.line, self.winner, self.winline = 0, Mark.DRAW, WinLine.DRAW
            return True
        return False
                
def initialize_screen(screen):
    # Fill the screen with background color
    pygame.draw.rect(screen, 'lightgray', (0, 0, WIDTH, HEIGHT))
    
    # Create board on a screen
    board = Board(screen)
    board.render()
    return board, Mark.CROSS, False, False, False
    

def main():
    global FONT
    # Create game window
    pygame.init()
    pygame.display.set_caption("Tic-Tac-Toe")
    size = (WIDTH, HEIGHT)
    screen = pygame.display.set_mode(size)
    
    FONT = pygame.font.Font(None, FONT_SIZE)
    '''
    "board" is a game board
    "turn" Defines which player turn is
    "end" checks if game is finished
    "mark_success" checks if mark placed on board correctly
    "restart" checks if players want to restart the game
    '''
    board, turn, end, mark_success, restart = initialize_screen(screen)
    
    # If game continues
    running = True
    while running:
        if restart:
            board, turn, end, mark_success, restart = initialize_screen(screen)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not end and event.type == pygame.MOUSEBUTTONDOWN:
                mark_success = board.set_mark(turn)
            if end and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                restart = True
        '''
        if win:
            print("WINNER")
            pass
        else:
        '''
        if end:
            print("END")
            pass
        else:
            if mark_success:
                if turn == Mark.CIRCLE:
                    turn = Mark.CROSS
                else:
                    turn = Mark.CIRCLE
                mark_success = False
                end = board.check_game_end()
        board.render()
        pygame.display.flip()
    
    pygame.quit()
    
    
if __name__ == '__main__':
    main()