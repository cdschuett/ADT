import constants as c
import pygame
from pygame.locals import *
import pygame.gfxdraw


class MenuSprites():
    def __init__(self):
        self.mode = "null"
        self.reset = False
        self.check = False
        self.test_button = pygame.Rect(c.quarter, c.row_one, (c.t_quarter - c.quarter), (c.row_two-c.row_one))
        self.mcdu_button = pygame.Rect(c.quarter, c.row_three, (c.t_quarter - c.quarter), (c.row_two-c.row_one))
        self.eicas_button = pygame.Rect(c.quarter, c.row_five, (c.t_quarter - c.quarter), (c.row_six-c.row_five))
        self.chip_status = pygame.Rect(c.col_one, c.row_one, 20, 20)
        self.ready_status = pygame.Rect(c.col_one, c.row_one + 30, 20, 20)
        self.reset_button = pygame.Rect(c.quarter, c.row_five, 100, 100)
        self.check_rx_button = pygame.Rect(c.quarter + 110, c.row_five, 100, 100)
        self.mainMenu_button = pygame.Rect(c.col_four, c.row_six, 100, 100)

        #Rx Channels
        self.ch0_rx_status = pygame.Rect(c.col_two, c.row_one, 20, 20)
        self.ch1_rx_status = pygame.Rect(c.col_two, c.row_one + 30, 20, 20)
        self.ch2_rx_status = pygame.Rect(c.col_two, c.row_one + 60, 20, 20)
        self.ch3_rx_status = pygame.Rect(c.col_two, c.row_one + 90, 20, 20)
        self.ch4_rx_status = pygame.Rect(c.col_two, c.row_one + 120, 20, 20)
        self.ch5_rx_status = pygame.Rect(c.col_two, c.row_one + 150, 20, 20)
        self.ch6_rx_status = pygame.Rect(c.col_two, c.row_one + 180, 20, 20)
        self.ch7_rx_status = pygame.Rect(c.col_two, c.row_one + 210, 20, 20)

        #Tx Channels
        self.ch0_tx_status = pygame.Rect(c.col_three, c.row_one, 20, 20)
        self.ch1_tx_status = pygame.Rect(c.col_three, c.row_one + 30, 20, 20)
        self.ch2_tx_status = pygame.Rect(c.col_three, c.row_one + 60, 20, 20)
        self.ch3_tx_status = pygame.Rect(c.col_three, c.row_one + 90, 20, 20)


    def get_mode(self):
        return(self.mode)
    def set_mode(self, mode):
        self.mode = mode
    
    def get_reset(self):
        if self.reset:
            self.reset = False
            return True
        else:
            return self.reset

    def get_check(self):
        if self.check:
            self.check = False
            return True
        else:
            return self.reset

    def update(self, events):
        if self.mode == "menu":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.test_button.collidepoint(event.pos):
                        self.mode = "test"
                    elif self.mcdu_button.collidepoint(event.pos):
                        self.mode = "mcdu"
                    elif self.eicas_button.collidepoint(event.pos):
                        self.mode = "eicas"
        elif self.mode == "test":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.reset_button.collidepoint(event.pos):
                        self.reset = True
                    elif self.check_rx_button.collidepoint(event.pos):
                        self.check = True
                    elif self.mainMenu_button.collidepoint(event.pos):
                        self.mode = "menu"
        elif self.mode == "mcdu":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.mainMenu_button.collidepoint(event.pos):
                        self.mode = "menu"



    def mainMenu(self, screen):
        super().__init__() 

        mouse = pygame.mouse.get_pos()

        pygame.draw.rect(screen, c.GREY if self.test_button.collidepoint(mouse) else c.BLUE, self.test_button)
        pygame.draw.rect(screen, c.GREY if self.mcdu_button.collidepoint(mouse) else c.BLUE, self.mcdu_button)
        pygame.draw.rect(screen, c.GREY if self.eicas_button.collidepoint(mouse) else c.BLUE, self.eicas_button)

        self.font = pygame.font.SysFont("Arial", 40, bold=True)

        text_data = [
        {"text": "TEST MODE", "color": c.GREEN, "pos": (c.half, ((c.row_two - c.row_one)/2)+c.row_one)},
        {"text": "MCDU MODE", "color": c.GREEN, "pos": (c.half, ((c.row_four - c.row_three)/2)+c.row_three)},
        {"text": "EICAS MODE", "color": c.GREEN, "pos": (c.half, ((c.row_six - c.row_five)/2)+c.row_five)}
        ]
        for item in text_data:
            text_surface = self.font.render(item["text"], True, item["color"])
            text_rect = text_surface.get_rect(center=item["pos"])
            screen.blit(text_surface, text_rect)

    def testMenu(self, screen, chip, ready, rxStatus, txStatus):
        super().__init__() 

        mouse = pygame.mouse.get_pos()

        pygame.draw.rect(screen, c.GREEN if chip else c.RED, self.chip_status)
        pygame.draw.rect(screen, c.GREEN if ready else c.RED, self.ready_status)
        pygame.draw.rect(screen, c.GREEN if rxStatus[0] else c.RED, self.ch0_rx_status)
        pygame.draw.rect(screen, c.GREEN if rxStatus[1] else c.RED, self.ch1_rx_status)
        pygame.draw.rect(screen, c.GREEN if rxStatus[2] else c.RED, self.ch2_rx_status)
        pygame.draw.rect(screen, c.GREEN if rxStatus[3] else c.RED, self.ch3_rx_status)
        pygame.draw.rect(screen, c.GREEN if rxStatus[4] else c.RED, self.ch4_rx_status)
        pygame.draw.rect(screen, c.GREEN if rxStatus[5] else c.RED, self.ch5_rx_status)
        pygame.draw.rect(screen, c.GREEN if rxStatus[6] else c.RED, self.ch6_rx_status)
        pygame.draw.rect(screen, c.GREEN if txStatus[0] else c.RED, self.ch0_tx_status)
        pygame.draw.rect(screen, c.GREEN if txStatus[1] else c.RED, self.ch1_tx_status)
        pygame.draw.rect(screen, c.GREEN if txStatus[2] else c.RED, self.ch2_tx_status)
        pygame.draw.rect(screen, c.GREEN if txStatus[3] else c.RED, self.ch3_tx_status)

        pygame.draw.rect(screen, c.BLUE if self.reset_button.collidepoint(mouse) else c.RED, self.reset_button)
        pygame.draw.rect(screen, c.BLUE if self.check_rx_button.collidepoint(mouse) else c.RED, self.check_rx_button)
        pygame.draw.rect(screen, c.BLUE if self.mainMenu_button.collidepoint(mouse) else c.RED, self.mainMenu_button)

        self.font = pygame.font.SysFont("Arial", 20)

        text_data = [
        {"text": "Chip Status", "color": c.WHITE, "pos": (c.col_one + 22, c.row_one)},
        {"text": "Rx0 Status", "color": c.WHITE, "pos": (c.col_two + 22, c.row_one)},
        {"text": "Rx1 Status", "color": c.WHITE, "pos": (c.col_two + 22, c.row_one + 30)},
        {"text": "Rx2 Status", "color": c.WHITE, "pos": (c.col_two + 22, c.row_one + 60)},
        {"text": "Rx3 Status", "color": c.WHITE, "pos": (c.col_two + 22, c.row_one + 90)},
        {"text": "Rx4 Status", "color": c.WHITE, "pos": (c.col_two + 22, c.row_one + 120)},
        {"text": "Rx5 Status", "color": c.WHITE, "pos": (c.col_two + 22, c.row_one + 150)},
        {"text": "Rx6 Status", "color": c.WHITE, "pos": (c.col_two + 22, c.row_one + 180)},
        {"text": "Rx7 Status", "color": c.WHITE, "pos": (c.col_two + 22, c.row_one + 210)},
        {"text": "Tx0 Status", "color": c.WHITE, "pos": (c.col_three + 22, c.row_one)},
        {"text": "Tx1 Status", "color": c.WHITE, "pos": (c.col_three + 22, c.row_one + 30)},
        {"text": "Tx2 Status", "color": c.WHITE, "pos": (c.col_three + 22, c.row_one + 60)},
        {"text": "Tx3 Status", "color": c.WHITE, "pos": (c.col_three + 22, c.row_one + 90)},
        {"text": "Ready", "color": c.WHITE, "pos": (c.col_one + 22, c.row_one + 30)},
        {"text": "Reset", "color": c.WHITE, "pos": (c.quarter + 25, c.row_five + 10)},
        {"text": "Check", "color": c.WHITE, "pos": (c.quarter + 135, c.row_five + 10)},
        {"text": "Main", "color": c.WHITE, "pos": (c.col_four + 10, c.row_six + 10)}
        ]
        for item in text_data:
            text_surface = self.font.render(item["text"], True, item["color"])
            text_rect = text_surface.get_rect(topleft=item["pos"])
            screen.blit(text_surface, text_rect)

    def mcduMenu(self, screen):
        super().__init__() 

        mouse = pygame.mouse.get_pos()

        pygame.draw.rect(screen, c.BLUE if self.mainMenu_button.collidepoint(mouse) else c.RED, self.mainMenu_button)

        self.font = pygame.font.SysFont("Arial", 20)

        text_data = [
        {"text": "Use MCDU", "color": c.WHITE, "pos": (c.col_one + 22, c.row_one)},
        {"text": "Main", "color": c.WHITE, "pos": (c.col_four + 10, c.row_six + 10)}
        ]
        for item in text_data:
            text_surface = self.font.render(item["text"], True, item["color"])
            text_rect = text_surface.get_rect(topleft=item["pos"])
            screen.blit(text_surface, text_rect)

    def getData(self, screen, chip, ready, rxStatus):
        super().__init__() 
