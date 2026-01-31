import pygame

#Framerate
FPS = 24

# Predefined some colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREY = (128, 128, 128)

# Screen dimensions
#SCREEN_WIDTH = 720
#SCREEN_HEIGHT = 1000
pygame.display.init()
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h

SQUARE_SIZE = 40
RADIUS1 = 55
RADIUS2 = 35
#Alignment Vectors
half = int(SCREEN_WIDTH/2)
quarter = int(SCREEN_WIDTH/4)
t_quarter = int(3*SCREEN_WIDTH/4)
v_y_divider = int(SCREEN_HEIGHT*0.05)
hl_x_divider = int(SCREEN_WIDTH*0.05)
hl_y_divider = int(3*SCREEN_HEIGHT/4)
hr_x_divider = int(SCREEN_WIDTH*0.55)
hr_y_divider = int(2*SCREEN_HEIGHT/3)
col_one = int(SCREEN_WIDTH/8)
col_two = int(3*SCREEN_WIDTH/8)
col_three = int(5*SCREEN_WIDTH/8)
col_four = int(7*SCREEN_WIDTH/8)
row_one = int(3*SCREEN_HEIGHT/24)
row_two = int(7*SCREEN_HEIGHT/24)
row_three = int(11*SCREEN_HEIGHT/24)
row_four = int(15*SCREEN_HEIGHT/24)
row_five = int(19*SCREEN_HEIGHT/24)
row_six = int(22*SCREEN_HEIGHT/24)
