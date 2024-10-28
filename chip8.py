from chip8screen import Screen
import pygame
import time

class chip8:
    def __init__(self, path):
        self.path = path
        self.memory = [0] * 4096
        self.v = [0] * 16
        self.PC = 0x200
        self.I = 0
        self.allocatefont()

        self.run = True

        self.display = Screen()

    def startgame(self):
        while self.run:
            self.loadrom()
            self.executeopcode()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            pygame.display.update()
            time.sleep(1/60)
        pygame.quit()

    def allocatefont(self):
        font = [0xF0, 0x90, 0x90, 0x90, 0xF0,
                0x20, 0x60, 0x20, 0x20, 0x70,
                0xF0, 0x10, 0xF0, 0x80, 0xF0,
                0xF0, 0x10, 0xF0, 0x10, 0xF0,
                0x90, 0x90, 0xF0, 0x10, 0x10,
                0xF0, 0x80, 0xF0, 0x10, 0xF0,
                0xF0, 0x80, 0xF0, 0x90, 0xF0,
                0xF0, 0x10, 0x20, 0x40, 0x40, 
                0xF0, 0x90, 0xF0, 0x90, 0xF0,
                0xF0, 0x90, 0xF0, 0x10, 0xF0,
                0xF0, 0x90, 0xF0, 0x90, 0x90,
                0xE0, 0x90, 0xE0, 0x90, 0xE0, 
                0xF0, 0x80, 0x80, 0x80, 0xF0,
                0xE0, 0x90, 0x90, 0x90, 0xE0,
                0xF0, 0x80, 0xF0, 0x80, 0xF0,
                0xF0, 0x80, 0xF0, 0x80, 0x80]
        fontpos = 0
        for i in range(0x50, 0x9F):
            self.memory[i] = font[fontpos]
            fontpos+=1

    def loadrom(self):
        file = open(self.path,"rb")
        for i in range(0x200, len(self.memory)):
            byte = file.read(1)
            if not byte:
                break
            self.memory[i] = int.from_bytes(byte, byteorder='big')

    def fetchopcode(self):
        opcode = self.memory[self.PC] << 8 | self.memory[self.PC + 1]
        self.PC+=2
        return opcode
    
    def executeopcode(self):
        opcode = self.fetchopcode()
        n1 = opcode & 0xF000
        n2 = opcode & 0x0F00
        n3 = opcode & 0x00F0
        n4 = opcode & 0x000F

        #Clear display (00E0)
        if opcode == 0x00E0:
            for X in range(self.display.SCREEN_HEIGHT):
                for Y in range(self.display.SCREEN_WIDTH):
                    self.display.pixel_array[Y,X] = (0,0,0)
            pygame.display.flip()
        
        #Make PC jump to NNN position (1NNN)
        elif n1 == 0x1000:
            jump_pos = n2 + n3 + n4
            self.PC = jump_pos

        #Change register value at x position (6XNN)
        elif n1 == 0x6000:
            value = n3 + n4
            pos = n2 >> 8
            self.v[pos] = value

        #Add register value at x position (7XNN)
        elif n1 == 0x7000:
            value = n3 + n4
            pos = n2 >> 8
            self.v[pos] += value

        #Set index register I (AXNNN)
        elif n1 == 0xA000:
            value = n2 + n3 + n4
            self.I = value

        #Draw instruction (DXYN)
        elif n1 == 0xD000:
            self.v[0xF] = 0
            x_access = self.v[n2 >> 8] % 64
            y_access = self.v[n3 >> 4] % 32
            xcoordinate = x_access
            ycoordinate = y_access
            spriteheight =  n4

            for Y in range(spriteheight):
                nthspritebyte = self.memory[self.I + Y]
                print(nthspritebyte)
                if ycoordinate < self.display.SCREEN_HEIGHT:
                    for X in range(8):
                            bit = (nthspritebyte >> (7 - X)) & 0x01
                            if xcoordinate < self.display.SCREEN_WIDTH:
                                if self.display.pixel_array[xcoordinate,ycoordinate] == 1 and bit == 1:
                                    self.display.pixel_array[xcoordinate,ycoordinate] = (0,0,0)
                                    self.v[0xF] = 1
                                elif self.display.pixel_array[xcoordinate,ycoordinate] == 0 and bit == 1:
                                    self.display.pixel_array[xcoordinate,ycoordinate] = (255,255,255)
                            xcoordinate+=1
                ycoordinate+=1
                xcoordinate = x_access
            pygame.display.flip()


c8 = chip8("E:/CHIP-8/Chip-8-Python-Project/roms/IBM Logo.ch8")
c8.startgame()
