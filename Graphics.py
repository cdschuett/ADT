import constants as c
import pygame, sys
from pygame.locals import *
import pygame.gfxdraw


class GFXDrawCircleSprite():
    def __init__(self):
        pass

    def dialScale(self, x, orgmin, orgmax, newmin, newmax):
        scaled_x = ((x - orgmin) / (orgmax - orgmin)) * (newmax - newmin) + newmin
        return(scaled_x)

    def eicasComponents(self, screen):
        super().__init__() 

        # Draw Vertical Divider
        pygame.gfxdraw.box(screen, (c.half, c.v_y_divider, 3, 750), c.GREEN)

        # Draw Left Horizontal Divider
        pygame.gfxdraw.box(screen, (c.hl_x_divider, c.hl_y_divider, 290, 3), c.GREEN)

        # Draw Right Horizontal Divider
        pygame.gfxdraw.box(screen, (c.hr_x_divider, c.hr_y_divider, 290, 3), c.GREEN)

        #FADEC Indicator
        pygame.gfxdraw.filled_polygon(screen, [(650,10), (670,10), (670,30), (650,30)], c.RED)

        # Engine Data
        # Draw N1 Engine 1
        pygame.gfxdraw.arc(screen, c.col_one, c.row_one, c.RADIUS1, 0, 245, c.WHITE)
        pygame.gfxdraw.rectangle(screen, ((c.col_one + 10), (c.row_one - c.RADIUS1 - 5), 60, 40), c.WHITE)
        pygame.gfxdraw.hline(screen, (c.col_one + c.RADIUS1), (c.col_one + c.RADIUS1 + 5), c.row_one, c.WHITE)
        pygame.gfxdraw.line(screen, c.col_one - 24, c.row_one - 50, c.col_one - 28, c.row_one - 60, c.RED)
        pygame.gfxdraw.line(screen, c.col_one - 31, c.row_one - 45, c.col_one - 36, c.row_one - 55, c.YELLOW)


        # Draw N1 Engine 2
        pygame.gfxdraw.arc(screen, c.col_two, c.row_one, c.RADIUS1, 0, 245, c.WHITE)
        pygame.gfxdraw.rectangle(screen, ((c.col_two + 10), (c.row_one - c.RADIUS1 - 5), 60, 40), c.WHITE)
        pygame.gfxdraw.hline(screen, (c.col_two + c.RADIUS1), (c.col_two + c.RADIUS1 + 5), c.row_one, c.WHITE)
        pygame.gfxdraw.line(screen, c.col_two - 24, c.row_one - 50, c.col_two - 28, c.row_one - 60, c.RED)
        pygame.gfxdraw.line(screen, c.col_two - 31, c.row_one - 45, c.col_two - 36, c.row_one - 55, c.YELLOW)


        # Draw EGT Engine 1
        pygame.gfxdraw.arc(screen, c.col_one, c.row_two, 55, 0, 245, c.WHITE)
        pygame.gfxdraw.rectangle(screen, ((c.col_one + 10), (c.row_two - c.RADIUS1 - 5), 60, 40), c.WHITE)
        pygame.gfxdraw.hline(screen, (c.col_one + c.RADIUS1), (c.col_one + c.RADIUS1 + 5), c.row_two, c.WHITE)
        pygame.gfxdraw.line(screen, c.col_one - 24, c.row_two - 50, c.col_one - 28, c.row_two - 60, c.RED)
        pygame.gfxdraw.line(screen, c.col_one - 31, c.row_two - 45, c.col_one - 36, c.row_two - 55, c.YELLOW)

        # Draw EGT Engine 2
        pygame.gfxdraw.arc(screen, c.col_two, c.row_two, 55, 0, 245, c.WHITE)
        pygame.gfxdraw.rectangle(screen, ((c.col_two + 10), (c.row_two - c.RADIUS1 - 5), 60, 40), c.WHITE)
        pygame.gfxdraw.hline(screen, (c.col_two + c.RADIUS1), (c.col_two + c.RADIUS1 + 5), c.row_two, c.WHITE)
        pygame.gfxdraw.line(screen, c.col_two - 24, c.row_two - 50, c.col_two - 28, c.row_two - 60, c.RED)
        pygame.gfxdraw.line(screen, c.col_two - 31, c.row_two - 45, c.col_two - 36, c.row_two - 55, c.YELLOW)

        # Draw N2 Engine 1
        pygame.gfxdraw.arc(screen, c.col_one, c.row_three, 55, 0, 245, c.WHITE)
        pygame.gfxdraw.rectangle(screen, ((c.col_one + 10), (c.row_three - c.RADIUS1 - 5), 60, 40), c.WHITE)
        pygame.gfxdraw.hline(screen, (c.col_one + c.RADIUS1), (c.col_one + c.RADIUS1 + 5), c.row_three, c.WHITE)
        pygame.gfxdraw.line(screen, c.col_one - 24, c.row_three - 50, c.col_one - 28, c.row_three - 60, c.RED)
        pygame.gfxdraw.line(screen, c.col_one - 31, c.row_three - 45, c.col_one - 36, c.row_three - 55, c.YELLOW)

        # Draw N2 Engine 2
        pygame.gfxdraw.arc(screen, c.col_two, c.row_three, 55, 0, 245, c.WHITE)
        pygame.gfxdraw.rectangle(screen, ((c.col_two + 10), (c.row_three - c.RADIUS1 - 5), 60, 40), c.WHITE)
        pygame.gfxdraw.hline(screen, (c.col_two + c.RADIUS1), (c.col_two + c.RADIUS1 + 5), c.row_three, c.WHITE)
        pygame.gfxdraw.line(screen, c.col_two - 24, c.row_three - 50, c.col_two - 28, c.row_three - 60, c.RED)
        pygame.gfxdraw.line(screen, c.col_two - 31, c.row_three - 45, c.col_two - 36, c.row_three - 55, c.YELLOW)

        # Draw FF/FU Engine 1
        pygame.gfxdraw.arc(screen, c.col_one, c.row_four, 55, 0, 245, c.WHITE)
        pygame.gfxdraw.rectangle(screen, ((c.col_one + 10), (c.row_four - c.RADIUS1 - 5), 60, 40), c.WHITE)
        pygame.gfxdraw.hline(screen, (c.col_one + c.RADIUS1), (c.col_one + c.RADIUS1 + 5), c.row_four, c.WHITE)
        pygame.gfxdraw.line(screen, c.col_one - 24, c.row_four - 50, c.col_one - 28, c.row_four - 60, c.RED)

        # Draw FF/FU Engine 2
        pygame.gfxdraw.arc(screen, c.col_two, c.row_four, 55, 0, 245, c.WHITE)
        pygame.gfxdraw.rectangle(screen, ((c.col_two + 10), (c.row_four - c.RADIUS1 - 5), 60, 40), c.WHITE)
        pygame.gfxdraw.hline(screen, (c.col_two + c.RADIUS1), (c.col_two + c.RADIUS1 + 5), c.row_four, c.WHITE)
        pygame.gfxdraw.line(screen, c.col_two - 24, c.row_four - 50, c.col_two - 28, c.row_four - 60, c.RED)

        # Oil and Vibration
        # Oil Pressure Left
        pygame.gfxdraw.arc(screen, c.col_three, c.row_one, c.RADIUS2, 40, 320, c.WHITE)
        pygame.gfxdraw.pie(screen, c.col_three, c.row_one, c.RADIUS2+10, 40, 40, c.WHITE)
        pygame.gfxdraw.pie(screen, c.col_three, c.row_one, c.RADIUS2+10, 320, 320, c.WHITE)
        pygame.gfxdraw.filled_trigon(screen, c.col_three, c.row_one, c.col_three+25, c.row_one+24, c.col_three+25, c.row_one-24, c.BLACK)

        # Oil Pressure Right
        pygame.gfxdraw.arc(screen, c.col_four, c.row_one, c.RADIUS2, 40, 320, c.WHITE)
        pygame.gfxdraw.pie(screen, c.col_four, c.row_one, c.RADIUS2+10, 40, 40, c.WHITE)
        pygame.gfxdraw.pie(screen, c.col_four, c.row_one, c.RADIUS2+10, 320, 320, c.WHITE)
        pygame.gfxdraw.filled_trigon(screen, c.col_four, c.row_one, c.col_four+25, c.row_one+24, c.col_four+25, c.row_one-24, c.BLACK)

        # Oil Temp Left
        pygame.gfxdraw.arc(screen, c.col_three, c.row_two, c.RADIUS2, 40, 320, c.WHITE)

        # Oil Temp Right
        pygame.gfxdraw.arc(screen, c.col_four, c.row_two, c.RADIUS2, 40, 320, c.WHITE)

        # Oil Quantity Left
        pygame.gfxdraw.rectangle(screen, (c.col_three - c.RADIUS2, c.row_three - c.RADIUS2, 60, 40), c.WHITE)

        # Oil Quantity Right
        pygame.gfxdraw.rectangle(screen, (c.col_four - c.RADIUS2, c.row_three - c.RADIUS2, 60, 40), c.WHITE)

        # Vibration Left
        pygame.gfxdraw.arc(screen, c.col_three, c.row_four - 25, 35, 110, 370, c.WHITE)

        # Vibration Right
        pygame.gfxdraw.arc(screen, c.col_four, c.row_four - 25, 35, 110, 370, c.WHITE)

        # Hydraulic Pressure and Quantity
        # Hyd Press Left
        pygame.gfxdraw.arc(screen, c.col_three, c.row_six, c.RADIUS1, 40, 320, c.WHITE)

        # Hyd Press Right
        pygame.gfxdraw.arc(screen, c.col_four, c.row_six, c.RADIUS1, 40, 320, c.WHITE)

        # Hyd Quantity Left
        pygame.gfxdraw.rectangle(screen, (c.col_three, c.row_six, 60, 40), c.WHITE)

        # Hyd Quantity Right
        pygame.gfxdraw.rectangle(screen, (c.col_four, c.row_six, 60, 40), c.WHITE)

        # Fuel Quantity and Balance
        # Fuel Left
        pygame.gfxdraw.arc(screen, c.col_one, c.row_six, c.RADIUS2, 140, 395, c.WHITE)
        pygame.gfxdraw.pie(screen, c.col_one, c.row_six, c.RADIUS2+10, 140, 395, c.WHITE)

        # Fuel Center
        pygame.gfxdraw.arc(screen, c.quarter, (c.row_six - 60), c.RADIUS2+10, 140, 395, c.WHITE)
        pygame.gfxdraw.pie(screen, c.quarter, (c.row_six - 60), c.RADIUS2+20, 140, 395, c.WHITE)

        # Fuel Right
        pygame.gfxdraw.arc(screen, c.col_two, c.row_six, c.RADIUS2, 140, 395, c.WHITE)
        pygame.gfxdraw.pie(screen, c.col_two, c.row_six, c.RADIUS2+10, 140, 395, c.WHITE)


    def draw(self, screen):
        self.eicasComponents(screen)

    def drawDials(self, screen, sensors):
        super().__init__() 

        # Fadec Status
        if sensors.readFadecStatus():
            pygame.gfxdraw.filled_polygon(screen, [(650,10), (670,10), (670,30), (650,30)], c.GREEN)

        # Engine Data
        # Draw N1 Engine 1
        dial = round(self.dialScale(sensors.readN1Left(), 0, 100, 0, 245))
        pygame.gfxdraw.pie(screen, c.col_one, c.row_one, c.RADIUS1, dial, dial, c.WHITE) # 0-245

        # Draw N1 Engine 2
        dial = round(self.dialScale(sensors.readN1Right(), 0, 100, 0, 245))
        pygame.gfxdraw.pie(screen, c.col_two, c.row_one, c.RADIUS1, dial, dial, c.WHITE) #0-245

        # Draw EGT Engine 1
        dial = round(self.dialScale(sensors.readEgtLeft(), 0, 1000, 0, 245))
        pygame.gfxdraw.pie(screen, c.col_one, c.row_two, c.RADIUS1, dial, dial, c.WHITE)

        # Draw EGT Engine 2
        dial = round(self.dialScale(sensors.readEgtRight(), 0, 1000, 0, 245))
        pygame.gfxdraw.pie(screen, c.col_two, c.row_two, c.RADIUS1, dial, dial, c.WHITE)

        # Draw N2 Engine 1
        dial = round(self.dialScale(sensors.readN2Left(), 0, 100, 0, 245))
        pygame.gfxdraw.pie(screen, c.col_one, c.row_three, c.RADIUS1, dial, dial, c.WHITE)

        # Draw N2 Engine 2
        dial = round(self.dialScale(sensors.readN2Right(), 0, 100, 0, 245))
        pygame.gfxdraw.pie(screen, c.col_two, c.row_three, c.RADIUS1, dial, dial, c.WHITE)

        # Draw FF/FU Engine 1
        dial = round(self.dialScale(sensors.readFFULeft(), 0, 6, 0, 245))
        pygame.gfxdraw.pie(screen, c.col_one, c.row_four, c.RADIUS1, dial, dial, c.WHITE)


        # Draw FF/FU Engine 2
        dial = round(self.dialScale(sensors.readFFURight(), 0, 6, 0, 245))
        pygame.gfxdraw.pie(screen, c.col_two, c.row_four, c.RADIUS1, dial, dial, c.WHITE)

        # Oil and Vibration
        # Oil Pressure Left
        dial = round(self.dialScale(sensors.readN2Left(), 0, 100, 40, 320))
        pygame.gfxdraw.pie(screen, c.col_three, c.row_one, c.RADIUS2, dial, dial, c.WHITE)


        # Oil Pressure Right
        pygame.gfxdraw.arc(screen, c.col_four, c.row_one, 35, 40, 320, c.WHITE)

        # Oil Temp Left
        pygame.gfxdraw.arc(screen, c.col_three, c.row_two, 35, 40, 320, c.WHITE)

        # Oil Temp Right
        pygame.gfxdraw.arc(screen, c.col_four, c.row_two, 35, 40, 320, c.WHITE)

        # Vibration Left
        dial = round(self.dialScale(sensors.readN2Left(), 0, 100, 110, 370))
        pygame.gfxdraw.pie(screen, c.col_three, c.row_four - 25, c.RADIUS2, dial, dial, c.WHITE)

        # Vibration Right
        dial = round(self.dialScale(sensors.readN2Left(), 0, 100, 110, 370))
        pygame.gfxdraw.pie(screen, c.col_four, c.row_four - 25, c.RADIUS2, dial, dial, c.WHITE)

        # Hydraulic Pressure and Quantity
        # Hyd Press Left
        pygame.gfxdraw.arc(screen, c.col_three, c.row_five, 55, 40, 320, c.WHITE)

        # Hyd Press Right
        pygame.gfxdraw.arc(screen, c.col_four, c.row_five, 55, 40, 320, c.WHITE)


        # Fuel Quantity and Balance
        # Fuel Left
        dial = round(self.dialScale(sensors.readLeftTank(), 0, 3000, 140, 395))
        pygame.gfxdraw.pie(screen, c.col_one, c.row_six, c.RADIUS2+10, dial, dial, c.WHITE)

        # Fuel Center
        dial = round(self.dialScale(sensors.readCenterTank(), 0, 10000, 140, 395))
        pygame.gfxdraw.pie(screen, c.quarter, (c.row_six - 60), c.RADIUS2+20, dial, dial, c.WHITE)

        # Fuel Right
        dial = round(self.dialScale(sensors.readRightTank(), 0, 3000, 140, 395))
        pygame.gfxdraw.pie(screen, c.col_two, c.row_six, c.RADIUS2+10, dial, dial, c.WHITE)
