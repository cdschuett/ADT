import constants as c
import menus as m
import chipTest as t
import pygame, sys
from pygame.locals import *
import pygame.gfxdraw
from Graphics import GFXDrawCircleSprite
import time
import sys

pygame.init()
pygame.font.init()

font = pygame.font.SysFont('Arial', 30)

FramePerSec = pygame.time.Clock()

DISPLAYSURF = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
#DISPLAYSURF = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
DISPLAYSURF.fill(c.BLACK)
pygame.display.set_caption("Main Menu")
pygame.mouse.set_visible(True) 


if __name__=="__main__":
    
    rxStatus = [False, False, False, False, False, False, False, False]
    txStatus = [False, False, False, False]
    mode = False
    reset = False
    rxTest = False
    DISPLAYSURF.fill(c.BLACK)
    MENU = m.MenuSprites()
    CHIP = t.ARINC()

    while True:
        events = pygame.event.get()
        for event in events:              

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        MENU.update(events)
        mode = MENU.get_mode()
        reset = MENU.get_reset()
        rxTest = MENU.get_check()

        if mode == "test":
            DISPLAYSURF.fill(c.BLACK)
            MENU.testElements(DISPLAYSURF, CHIP.isChipSetupComplete(), CHIP.isChipReady(), rxStatus)
            if reset:
                CHIP.resetChip()
            if rxTest:
                for i in range(7):
                    rxStatus[i] = CHIP.checkRxRegister(i)
        elif mode == "mcdu":
            DISPLAYSURF.fill(c.WHITE)
        elif mode == "eicas":
            DISPLAYSURF.fill(c.PURPLE)
        else:
            MENU.menuElements(DISPLAYSURF)

        # Update the display
        pygame.display.flip()

        FramePerSec.tick(c.FPS)