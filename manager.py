import constants as c
import menus as m
import chipTest as t
import pygame, sys
from pygame.locals import *
import pygame.gfxdraw
from Graphics import GFXDrawCircleSprite
from eicasDemo import SensorPack
from eicasDemo import TextElement
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
    mode = "menu"
    reset = False
    rxTest = False
    DISPLAYSURF.fill(c.BLACK)
    MENU = m.MenuSprites()
    MENU.mainMenu(DISPLAYSURF)
    CHIP = t.ARINC()
    EICAS = GFXDrawCircleSprite()
    EICASTEXT = TextElement()
    EICASSENSOR = SensorPack()

    MENU.set_mode("menu")
    while True:
        events = pygame.event.get()
        for event in events:              

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        mode = MENU.get_mode()
        MENU.update(events)

        if mode == "menu":
            DISPLAYSURF.fill(c.BLACK)
            MENU.mainMenu(DISPLAYSURF)
        elif mode == "test":
            DISPLAYSURF.fill(c.BLACK)
            MENU.testMenu(DISPLAYSURF, CHIP.isChipSetupComplete(), CHIP.isChipReady(), rxStatus, txStatus)
            reset = MENU.get_reset()
            rxTest = MENU.get_check()
            if reset:
                CHIP.resetChip()
                rxStatus = [False, False, False, False, False, False, False, False]
                txStatus = [False, False, False, False]
            if rxTest:
                for i in range(7):
                    rxStatus[i] = CHIP.checkRxRegister(i)
                for i in range(3):
                    txStatus[i] = CHIP.checkTxRegister(i)
        elif mode == "mcdu":
            DISPLAYSURF.fill(c.BLUE)
            MENU.mcduMenu(DISPLAYSURF)
            CHIP.ReadMCDUWords()
        elif mode == "eicas":
            DISPLAYSURF.fill(c.BLACK)
            CHIP.ReadDataWords(EICASSENSOR)
            EICAS.draw(DISPLAYSURF)
            EICASTEXT.drawScreenLabels(DISPLAYSURF)
            EICASTEXT.drawDialNums(DISPLAYSURF)
            EICASTEXT.drawSensorVals(DISPLAYSURF, EICASSENSOR)
            EICASTEXT.drawFuelVals(DISPLAYSURF, EICASSENSOR)
            EICAS.drawDials(DISPLAYSURF, EICASSENSOR)

        # Update the display
        pygame.display.flip()

        FramePerSec.tick(c.FPS)