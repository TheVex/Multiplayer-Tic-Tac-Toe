import pygame

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 150
CELL_OFFSET = 20
LINE_WIDTH = 10

BACKGROUND_COLOR = 'lightgray'
BOARD_COLOR = 'black'

class Board:
    def __init__(self):
        self.board = [['X' for _ in range(3)] for i in range(3)]
    
    def render(self, screen):
        start_pos = (WIDTH // 2 - int(CELL_SIZE * 1.5),
                     HEIGHT // 2 - int(CELL_SIZE * 1.5))                  
        pygame.draw.rect(screen, BOARD_COLOR, (start_pos[0], start_pos[1], 3, 3))
        for i in range(1, 3):
            pygame.draw.line(screen, BOARD_COLOR, 
                           (start_pos[0] + i * CELL_SIZE, start_pos[1]),
                           (start_pos[0] + i * CELL_SIZE, start_pos[1] + 3 * CELL_SIZE),
                           LINE_WIDTH)
            pygame.draw.line(screen, BOARD_COLOR, 
                           (start_pos[0], start_pos[1] + i * CELL_SIZE),
                           (start_pos[0] + 3 * CELL_SIZE, start_pos[1] + i * CELL_SIZE),
                           LINE_WIDTH)


        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 'X':
                    pygame.draw.line(screen, BOARD_COLOR,
                            (start_pos[0] + i * CELL_SIZE + CELL_OFFSET,
                             start_pos[1] + j * CELL_SIZE + CELL_OFFSET),
                            (start_pos[0] + (i + 1) * CELL_SIZE - CELL_OFFSET,
                             start_pos[1] + (j + 1) * CELL_SIZE - CELL_OFFSET),
                            LINE_WIDTH)
                    pygame.draw.line(screen, BOARD_COLOR,
                            (start_pos[0] + (i + 1) * CELL_SIZE - CELL_OFFSET,
                             start_pos[1] + j * CELL_SIZE + CELL_OFFSET),
                            (start_pos[0] + i * CELL_SIZE + CELL_OFFSET,
                             start_pos[1] + (j + 1) * CELL_SIZE - CELL_OFFSET),
                            LINE_WIDTH)
 
                            

def main():
    pygame.init()
    pygame.display.set_caption("Tic-Tac-Toe")
    size = (WIDTH, HEIGHT)
    screen = pygame.display.set_mode(size)
    
    pygame.draw.rect(screen, 'lightgray', (0, 0, WIDTH, HEIGHT))
    
    board = Board()
    board.render(screen)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
    
    pygame.quit()
    
    
if __name__ == '__main__':
    main()