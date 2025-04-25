import pygame
from enum import Enum


WIDTH = 800
HEIGHT = 600
CELL_SIZE = 150
CELL_OFFSET = 20
LINE_WIDTH = 10

BACKGROUND_COLOR = 'lightgray'
BOARD_COLOR = 'black'
CROSS_COLOR = 'red'
CIRCLE_COLOR = 'blue'


class Mark(Enum):
    CROSS = 1
    CIRCLE = 2
    
    
class WinLine(Enum):
    HORIZONTAL = 1
    VERTICAL = 2
    LEFT_DIAGONAL = 3
    RIGHT_DIAGONAL = 4
    
    
class Board:
    def __init__(self, screen):
        self.board = [[None for _ in range(3)] for i in range(3)]
        self.start_pos = (WIDTH // 2 - int(CELL_SIZE * 1.5),
                          HEIGHT // 2 - int(CELL_SIZE * 1.5))
        self.screen = screen  
    
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
    
    def set_winner(self, indicator, mark, line_type):
        if line_type == WinLine.HORIZONTAL:
            pygame.draw.line(self.screen, BOARD_COLOR,
                            (self.start_pos[0], self.start_pos[1] + int((indicator + 0.5) * CELL_SIZE)),
                            (self.start_pos[0] + 3 * CELL_SIZE), self.start_pos[1] + int((indicator + 0.5) * CELL_SIZE),
                            LINE_WIDTH)
        elif line_type == WinLine.VERTICAL:
            pygame.draw.line(self.screen, BOARD_COLOR,
                            (self.start_pos[0] + int((indicator + 0.5) * CELL_SIZE), self.start_pos[1]),
                            (self.start_pos[0] + int((indicator + 0.5) * CELL_SIZE), self.start_pos[1] + 3 * CELL_SIZE),
                            LINE_WIDTH)
        elif line_type == WinLine.LEFT_DIAGONAL:
            pygame.draw.line(self.screen, BOARD_COLOR, self.start_pos,
                             (self.start_pos[0] + 3 * CELL_SIZE, self.start_pos[1] + 3 * CELL_SIZE),
                             LINE_WIDTH)
        elif line_type == WinLine.RIGHT_DIAGONAL:
            pygame.draw.line(self.screen, BOARD_COLOR, 
                             (self.start_pos[0] + 3 * CELL_SIZE, self.start_pos[1]),
                             (self.start_pos[0], self.start_pos[1] + 3 * CELL_SIZE),
                             LINE_WIDTH)
        return True

        
        
        
    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == None: continue
            elif self.board[i][0] == self.board[i][1] == self.board[i][2]:
                return self.set_winner(i, self.board[i][0], WinLine.HORIZONTAL)
            elif self.board[0][i] == self.board[1][i] == self.board[2][i]:
                return self.set_winner(i, self.board[0][i], WinLine.VERTICAL)
        if self.board[0][0] is not None and self.board[0][0] == self.board[1][1] == self.board[2][2]:
            return self.set_winner(0, self.board[0][0], WinLine.LEFT_DIAGONAL)
        if self.board[0][2] is not None and self.board[0][2] == self.board[1][1] == self.board[2][0]:
            return self.set_winner(0, self.board[0][2], WinLine.RIGHT_DIAGONAL)
        return False
                


def main():
    pygame.init()
    pygame.display.set_caption("Tic-Tac-Toe")
    size = (WIDTH, HEIGHT)
    screen = pygame.display.set_mode(size)
    
    pygame.draw.rect(screen, 'lightgray', (0, 0, WIDTH, HEIGHT))
    
    board = Board(screen=screen)
    board.render()
    
    mark = Mark.CROSS
    win = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                success = board.set_mark(mark)
                if success:
                    if mark == Mark.CIRCLE:
                        mark = Mark.CROSS
                    else:
                        mark = Mark.CIRCLE
                    win = board.check_winner()
        board.render()
        pygame.display.flip()
    
    pygame.quit()
    
    
if __name__ == '__main__':
    main()