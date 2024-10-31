from chip8screen import Screen
import pygame
import time
import random
import threading

class chip8:
    def __init__(self, path, setvxvy):
        self.path = path
        self.setvxvy = setvxvy
        self.memory = [0] * 4096
        self.v = [0] * 16
        self.PC = 0x200
        self.stack = []
        self.delaytimer = 60
        self.soundtimer = 60
        self.I = 0
        self.allocatefont()
        self.keypad = {1: 0x1, 2: 0x2, 3: 0x3, 4: 0xC,
                       'q': 0x4, 'w': 0x5, 'e': 0x6, 'r': 0xD,
                        'a': 0x7, 's': 0x8, 'd': 0x9, 'f': 0xE,
                        'z': 0xA, 'x': 0x0, 'c': 0xB, 'v': 0xF,
                    }

        self.run = True
        self.key = 0
        self.display = Screen()

    def timers(self):
        while self.run:
            if self.delaytimer > 0:
                self.delaytimer -=1
            else:
                self.delaytimer = 60
            
            if self.soundtimer > 0:
                self.soundtimer -=1
            else:
                self.soundtimer = 60
            time.sleep(1/60)
        

    def keypressed(self):
        while self.run:
            key = pygame.key.get_pressed()
            if key[pygame.K_1] == True:
                self.key = 0x1
            elif key[pygame.K_2] == True:
                self.key = 0x2
            elif key[pygame.K_3]== True:
                self.key = 0x3
            elif key[pygame.K_4] == True:
                self.key = 0xC
            elif key[pygame.K_q] == True:
                self.key = 0x4
            elif key[pygame.K_w] == True:
                self.key = 0x5
            elif key[pygame.K_e] == True:
                self.key = 0x6
            elif key[pygame.K_r] == True:
                self.key = 0xD
            elif key[pygame.K_a] == True:
                self.key = 0x7
            elif key[pygame.K_s] == True:
                self.key = 0x8
            elif key[pygame.K_d] == True:
                self.key = 0x9
            elif key[pygame.K_f] == True:
                self.key = 0xE
            elif key[pygame.K_z] == True:
                self.key = 0xA
            elif key[pygame.K_x] == True:
                self.key = 0x0
            elif key[pygame.K_c] == True:
                self.key = 0xB
            elif key[pygame.K_v] == True:
                self.key = 0xF
            else:
                self.key = 0
            time.sleep(1/60)
            
    def startgame(self):
        timer_thread = threading.Thread(target=self.timers)
        timer_thread.daemon = True
        timer_thread.start()

        keypressed_thread = threading.Thread(target=self.keypressed)
        keypressed_thread.daemon = True
        keypressed_thread.start()

        self.loadrom()
        while self.run:
            self.executeopcode()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            pygame.display.update()
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
        for i in range(0x50, 0xA0):
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
        n2 = opcode & 0xF00
        n3 = opcode & 0xF0
        n4 = opcode & 0xF

        #Clear display (00E0)
        if opcode == 0x00E0:
            print("Running")
            for X in range(self.display.SCREEN_HEIGHT):
                for Y in range(self.display.SCREEN_WIDTH):
                    self.display.pixel_array[Y,X] = (0,0,0)
            pygame.display.flip()
        
        #Return subroutine from top of stack (00EE)
        elif opcode == 0x00EE:
            self.PC = self.stack.pop()
        
        #Make PC jump to NNN position (1NNN)
        elif n1 == 0x1000:
            jump_pos = n2 + n3 + n4
            self.PC = jump_pos

        #Append subroutine to stack and PC jumps to NNN position (2NNN)
        elif n1 == 0x2000:
            self.stack.append(self.PC)
            jump_pos = n2 + n3 + n4
            self.PC = jump_pos

        #Skip one instruction if register value at x position is equal to NN (3XNN)
        elif n1 == 0x3000:
            value = n3 + n4
            pos = n2 >> 8
            if self.v[pos] == value:
                self.PC += 2
        
        #Skip one instruction if register value at x position is not equal to NN (4XNN)
        elif n1 == 0x4000:
            value = n3 + n4
            pos = n2 >> 8
            if not self.v[pos] == value:
                self.PC += 2

        #Skip one instruction if register value at x position is equal to register value at y position (5XY0)
        elif n1 == 0x5000:
            x_pos = n2 >> 8
            y_pos = n3 >> 4

            if self.v[x_pos] == self.v[y_pos]:
                self.PC += 2
        
        #Skip one instruction if register value at x position is not equal to register value at y position (9XY0)
        elif n1 == 0x9000:
            x_pos = n2 >> 8
            y_pos = n3 >> 4

            if not self.v[x_pos] == self.v[y_pos]:
                self.PC += 2

        #Change register value at x position (6XNN)
        elif n1 == 0x6000:
            value = n3 + n4
            pos = n2 >> 8
            self.v[pos] = value

        #Add register value at x position (7XNN)
        elif n1 == 0x7000:
            value = n3 + n4
            pos = n2 >> 8
            self.v[pos] = (self.v[pos] + value) & 0xFF

        #Logical Operations (8XYN)
        elif n1 == 0x8000:
            x_pos = n2 >> 8
            y_pos = n3 >> 4

            #Set operation (8XY1)
            if n4 == 0:
                self.v[x_pos] = self.v[y_pos]
                
            #Binary OR operation (8XY1)    
            elif n4 == 1:
                self.v[x_pos] = self.v[x_pos] | self.v[y_pos]
            
            #Binary AND operation (8XY2)
            elif n4 == 2:
                self.v[x_pos] = self.v[x_pos] & self.v[y_pos]

            #Binary XOR operation (8XY3)
            elif n4 == 3:
                self.v[x_pos] = self.v[x_pos] ^ self.v[y_pos]

            #Add operation (8XY4)
            elif n4 == 4:
                self.v[x_pos] = self.v[x_pos] + self.v[y_pos] & 0xFF

                if self.v[x_pos] + self.v[y_pos] > 0xFF:
                    self.v[0xF] = 1
                else:
                    self.v[0xF] = 0

            #Subtract operation X-Y (8XY5)
            elif n4 == 5:
                self.v[x_pos] = self.v[x_pos] - self.v[y_pos] & 0xFF

                if self.v[x_pos] > self.v[y_pos]:
                    self.v[0xF] = 1
                else:
                    self.v[0xF] = 0

            #Subtract operation Y-X (8XY7)
            elif n4 == 7:
                self.v[x_pos] = self.v[y_pos] - self.v[x_pos] & 0xFF

                if self.v[y_pos] > self.v[x_pos]:
                    self.v[0xF] = 1
                else:
                    self.v[0xF] = 0

            #Bitwise right shift operation (8XY6) 
            elif n4 == 6:
                if self.setvxvy == True:
                    self.v[x_pos] = self.v[y_pos]

                self.v[0xF] = self.v[x_pos] & 1

                self.v[x_pos] = self.v[x_pos] >> 1 & 0xFF

            #Bitwise left shift operation (8XYE)
            elif n4 == 0xE:
                if self.setvxvy == True:
                    self.v[x_pos] = self.v[y_pos]

                self.v[0xF] = (self.v[x_pos] >> 7) & 1
                    
                self.v[x_pos] = self.v[x_pos] << 1 & 0xFF
                
        #Set index register I (ANNN)
        elif n1 == 0xA000:
            value = n2 + n3 + n4
            self.I = value

        #Jump with offset (BNNN)
        elif n1 == 0xB000:
            self.PC = n2 + n3 + n4 + self.v[0]

        #Generate random number (CXNN)
        elif n1 == 0xC000:
            pos = n2 >> 8
            self.v[pos] = random.randint(0,255) & (n3 + n4)

        #Skip if key 
        elif n1 == 0xE:
            pos = n2 >> 8

            #Skip if key is pressed (EX9E)
            if n3 == 0x90:
                if self.key == self.v[pos]:
                    self.PC+=2
                
            #Skip if not pressed (EXA1)
            elif n3 == 0xA0:
                if not self.key == self.v[pos]:
                    self.PC+=2
        
        elif n1 == 0xF000:
            pos = n2 >> 8
            fxnum = n3 + n4

            if fxnum == 0x07:
                self.v[pos] = self.delaytimer

            elif fxnum == 0x15:
                self.delaytimer = self.v[pos]

            elif fxnum == 0x18:
                self.soundtimer = self.v[pos]

            elif fxnum == 0x1E:
                self.I += self.v[pos]

            elif fxnum == 0x0A:
                print(self.key)
                while not self.key > 0:
                    self.PC -= 2
                self.v[pos] = self.key
            
            elif fxnum == 0x29:
                num = self.v[pos]

                if num == 0x0:
                    self.I = 0x50
                elif num == 0x1:
                    self.I = 0x55
                elif num == 0x2:
                    self.I = 0x5A
                elif num == 0x3:
                    self.I = 0x5F
                elif num == 0x4:
                    self.I = 0x64
                elif num == 0x5:
                    self.I = 0x69
                elif num == 0x6:
                    self.I = 0x6E
                elif num == 0x7:
                    self.I = 0x73
                elif num == 0x8:
                    self.I = 0x78
                elif num == 0x9:
                    self.I = 0x8D
                elif num == 0xA:
                    self.I = 0x82
                elif num == 0xB:
                    self.I = 0x87
                elif num == 0xC:
                    self.I = 0x8C
                elif num == 0xD:
                    self.I = 0x91
                elif num == 0xE:
                    self.I = 0x96
                elif num == 0xF:
                    self.I = 0x9B
            elif fxnum == 0x33:
                num = self.v[pos]
                int1 = num % 10
                num //= 10
                int2 = num % 10
                num //= 10
                int3 = num

                self.memory[self.I] = int1
                self.memory[self.I + 1] = int2
                self.memory[self.I + 2] = int3

            elif fxnum == 0x55:
                num = self.v[pos]
                for x in range(num):
                    self.memory[self.I + x] = self.v[x]

            elif fxnum == 0x65:
                num = self.v[pos]
                for x in range(num):
                    self.v[x] = self.memory[self.I + x]

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
        print(hex(opcode))
        time.sleep(1/700)


c8 = chip8("E:/CHIP-8/Chip-8-Python-Project/roms/test_opcode.ch8", False)
c8.startgame()
