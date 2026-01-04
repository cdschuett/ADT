import constants as c
import pygame
import sys

def create_checkerboard(surface, size, color1, color2):
    for y in range(0, surface.get_height(), size):
        for x in range(0, surface.get_width(), size):
            if (x // size) % 2 == (y // size) % 2:
                color = color1
            else:
                color = color2
            pygame.draw.rect(surface, color, (x, y, size, size))

def main():
    pygame.init()
    
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    pygame.display.set_caption("EICAS DISPLAY TEST PATTERN")
    clock = pygame.time.Clock()
    
    background = pygame.Surface(screen.get_size())
    create_checkerboard(background, c.SQUARE_SIZE, c.GREY, c.BLACK)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.blit(background, (0,0))
        
        pygame.display.flip()

        pygame.display.update()
        clock.tick(c.FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
