from chip8screen import Screen
import pygame
import time
import random
import threading
import os

class chip8:
    def __init__(self, path, setvxvy):
        self.path = path
        self.setvxvy = setvxvy
        self.memory = [0] * 4096
        self.v = [0] * 16
        self.PC = 0x200
        self.opcode = -1
        self.stack = []
        self.delaytimer = 0
        self.soundtimer = 0
        self.I = 0
        self.allocatefont()
        # self.keypad = {1: 0x1, 2: 0x2, 3: 0x3, 4: 0xC,
        #                'q': 0x4, 'w': 0x5, 'e': 0x6, 'r': 0xD,
        #                 'a': 0x7, 's': 0x8, 'd': 0x9, 'f': 0xE,
        #                 'z': 0xA, 'x': 0x0, 'c': 0xB, 'v': 0xF,
        #             }
        self.decode_table = {
            0x0000: self.n1_0_lookup,
            0x1000: self.jump_to_NNN,
            0x2000: self.jump_to_subroutine_NNN,
            0x3000: self.skip_if_reg_equals_NN,
            0x4000: self.skip_if_reg_not_equals_NN,
            0x5000: self.skip_if_reg_equals_y,
            0x6000: self.change_val_at_x,
            0x7000: self.add_reg_at_x,
            0x8000: self.n1_8_lookup,
            0x9000: self.skip_if_reg_not_equals_y,
            0xA000: self.set_I_NNN,
            0xB000: self.jump_with_offset,
            0xC000: self.gen_rand_num,
            0xE000: self.n1_E_lookup,
            0xF000: self.n1_F_lookup,
            0xD000: self.draw
        }

        self.x0table = {
            0x00E0: self.clear_display,
            0x00EE: self.return_subroutine
        }

        self.x8table = {
            0x0: self.set_operation,
            0x1: self.binary_or_operation,
            0x2: self.binary_and_operation,
            0x3: self.binary_xor_operation,
            0x4: self.add_operation,
            0x5: self.subtract_operationX_Y,
            0x6: self.right_shift_operation,
            0x7: self.subtract_operationY_X,
            0xE: self.left_shift_operation
        }

        self.xEtable = {
            0x90: self.skip_if_key_pressed,
            0xA0: self.skip_if_key_not_pressed
        }

        self.xFtable = {
            0x07: self.set_vx_to_delay_timer,
            0x15: self.set_delay_timer_to_vx,
            0x18: self.set_sound_timer_to_vx,
            0x1E: self.add_to_index,
            0x0A: self.get_key,
            0x29: self.set_font_pos,
            0x33: self.binary_decimal_conversion,
            0x55: self.store_memory,
            0x65: self.load_memory
        }

        self.run = True
        self.key = -1
        self.display = Screen()

        beeppath = os.path.join(os.getcwd(), "beep-08b.wav")
        self.beep = pygame.mixer.Sound(beeppath)

    def timers(self):
        while self.run:
            if self.delaytimer > 0:
                self.delaytimer -=1
            
            if self.soundtimer > 0:
                self.soundtimer -=1
                pygame.mixer.Sound.play(self.beep)
            
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
                self.key = -1
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
        self.opcode = self.memory[self.PC] << 8 | self.memory[self.PC + 1]
        self.PC+=2

    def executeopcode(self):
        self.fetchopcode()
        n1 = self.opcode & 0xF000

        if n1 in self.decode_table:
            self.decode_table[n1]()
        else:
            exit

        time.sleep(1/1000)

    def n1_0_lookup(self):
        self.x0table[self.opcode]()
    
    def n1_8_lookup(self):
        n4 = self.opcode & 0xF
        self.x8table[n4]()
    
    def n1_E_lookup(self):
        n3 = self.opcode & 0xF0
        self.xEtable[n3]()
    
    def n1_F_lookup(self):
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF
        self.xFtable[n3+n4]()


    def clear_display(self):
        for X in range(self.display.SCREEN_HEIGHT):
            for Y in range(self.display.SCREEN_WIDTH):
                self.display.pixel_array[Y,X] = (0,0,0)
        pygame.display.flip()
    
    def return_subroutine(self):
        self.PC = self.stack.pop()
    
    def jump_to_NNN(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF

        jump_pos = n2 + n3 + n4
        self.PC = jump_pos

    def jump_to_subroutine_NNN(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF

        self.stack.append(self.PC)
        jump_pos = n2 + n3 + n4
        self.PC = jump_pos

    def skip_if_reg_equals_NN(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF

        value = n3 + n4
        pos = n2 >> 8
        if self.v[pos] == value:
            self.PC += 2

    def skip_if_reg_equals_NN(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF

        value = n3 + n4
        pos = n2 >> 8
        if self.v[pos] == value:
            self.PC += 2
    def skip_if_reg_not_equals_NN(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF

        value = n3 + n4
        pos = n2 >> 8
        if not self.v[pos] == value:
            self.PC += 2
    def skip_if_reg_equals_y(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0

        x_pos = n2 >> 8
        y_pos = n3 >> 4

        if self.v[x_pos] == self.v[y_pos]:
            self.PC += 2
    def change_val_at_x(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF

        value = n3 + n4
        pos = n2 >> 8
        self.v[pos] = value
    
    def add_reg_at_x(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF
        
        value = n3 + n4
        pos = n2 >> 8
        self.v[pos] = (self.v[pos] + value) & 0xFF

    def set_operation(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0

        x_pos = n2 >> 8
        y_pos = n3 >> 4

        self.v[x_pos] = self.v[y_pos]
    
    def binary_or_operation(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0

        x_pos = n2 >> 8
        y_pos = n3 >> 4

        self.v[x_pos] = self.v[x_pos] | self.v[y_pos]

    def binary_and_operation(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0

        x_pos = n2 >> 8
        y_pos = n3 >> 4

        self.v[x_pos] = self.v[x_pos] & self.v[y_pos]
    
    def binary_xor_operation(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0

        x_pos = n2 >> 8
        y_pos = n3 >> 4

        self.v[x_pos] = self.v[x_pos] ^ self.v[y_pos]
    
    def add_operation(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0

        x_pos = n2 >> 8
        y_pos = n3 >> 4

        if self.v[x_pos] + self.v[y_pos] > 0xFF:
            self.v[x_pos] = self.v[x_pos] + self.v[y_pos] & 0xFF
            self.v[0xF] = 1
        else:
            self.v[x_pos] = self.v[x_pos] + self.v[y_pos] & 0xFF
            self.v[0xF] = 0
    
    def subtract_operationX_Y(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0

        x_pos = n2 >> 8
        y_pos = n3 >> 4

        if self.v[x_pos] >= self.v[y_pos]:
            self.v[x_pos] = self.v[x_pos] - self.v[y_pos] & 0xFF
            self.v[0xF] = 1
        else:
            self.v[x_pos] = self.v[x_pos] - self.v[y_pos] & 0xFF
            self.v[0xF] = 0
    
    def right_shift_operation(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0

        x_pos = n2 >> 8
        y_pos = n3 >> 4

        if self.setvxvy == True:
            self.v[x_pos] = self.v[y_pos]

        shifted_value = self.v[x_pos] & 1
        self.v[x_pos] = self.v[x_pos] >> 1 & 0xFF
        self.v[0xF] = shifted_value

    def subtract_operationY_X(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0

        x_pos = n2 >> 8
        y_pos = n3 >> 4

        if self.v[y_pos] >= self.v[x_pos]:
            self.v[x_pos] = self.v[y_pos] - self.v[x_pos] & 0xFF 
            self.v[0xF] = 1
        else:
            self.v[x_pos] = self.v[y_pos] - self.v[x_pos] & 0xFF 
            self.v[0xF] = 0
    
    def left_shift_operation(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0

        x_pos = n2 >> 8
        y_pos = n3 >> 4

        if self.setvxvy == True:
            self.v[x_pos] = self.v[y_pos]


        shifted_value = (self.v[x_pos] >> 7) & 1
        self.v[x_pos] = self.v[x_pos] << 1 & 0xFF
        self.v[0xF] = shifted_value
    
    def skip_if_reg_not_equals_y(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0

        x_pos = n2 >> 8
        y_pos = n3 >> 4

        if not self.v[x_pos] == self.v[y_pos]:
            self.PC += 2

    def set_I_NNN(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF

        value = n2 + n3 + n4
        self.I = value
    
    def jump_with_offset(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF

        self.PC = n2 + n3 + n4 + self.v[0]

    def gen_rand_num(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF

        pos = n2 >> 8
        self.v[pos] = random.randint(0,255) & (n3 + n4)
    
    def skip_if_key_pressed(self):
        n2 = self.opcode & 0xF00

        pos = n2 >> 8
        if self.key == self.v[pos]:
            self.PC+=2

    def skip_if_key_not_pressed(self):
        n2 = self.opcode & 0xF00

        pos = n2 >> 8
        if not self.key == self.v[pos]:
            self.PC+=2
             
    def set_vx_to_delay_timer(self):
        n2 = self.opcode & 0xF00
        pos = n2 >> 8

        self.v[pos] = self.delaytimer

    def set_delay_timer_to_vx(self):
        n2 = self.opcode & 0xF00
        pos = n2 >> 8

        self.delaytimer = self.v[pos]

    def set_sound_timer_to_vx(self):
        n2 = self.opcode & 0xF00
        pos = n2 >> 8

        self.soundtimer = self.v[pos]

    def add_to_index(self):
        n2 = self.opcode & 0xF00
        pos = n2 >> 8

        self.I += self.v[pos]

    def get_key(self):
        n2 = self.opcode & 0xF00
        pos = n2 >> 8

        while not self.key > -1:
            self.PC -= 2
        self.v[pos] = self.key

    def set_font_pos(self):
        n2 = self.opcode & 0xF00
        pos = n2 >> 8

        num = self.v[pos]
        nummap = {0x0:0x50,
                    0x1:0x55,
                    0x2:0x5A,
                    0x3:0x5F,
                    0x4:0x64,
                    0x5:0x69,
                    0x6:0x6E,
                    0x7:0x73,
                    0x8:0x78,
                    0x9:0x8D,
                    0xA:0x82,
                    0xB:0x87,
                    0xC:0x8C,
                    0xD:0x91,
                    0xE:0x96,
                    0xF:0x9B
                }
        self.I = nummap[num]
    
    def binary_decimal_conversion(self):
        n2 = self.opcode & 0xF00
        pos = n2 >> 8

        num = self.v[pos]
        int3 = num % 10
        num //= 10
        int2 = num % 10
        num //= 10
        int1 = num

        self.memory[self.I] = int1
        self.memory[self.I + 1] = int2
        self.memory[self.I + 2] = int3

    def store_memory(self):
        n2 = self.opcode & 0xF00
        pos = n2 >> 8

        for x in range(pos + 1):
            self.memory[self.I + x] = self.v[x]

    def load_memory(self):
        n2 = self.opcode & 0xF00
        pos = n2 >> 8

        for x in range(pos + 1):
            self.v[x] = self.memory[self.I + x]
    
    def draw(self):
        n2 = self.opcode & 0xF00
        n3 = self.opcode & 0xF0
        n4 = self.opcode & 0xF

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
                            if self.display.pixel_array[xcoordinate,ycoordinate] > 0 and bit == 1:
                                self.display.pixel_array[xcoordinate,ycoordinate] = (0,0,0)
                                self.v[0xF] = 1
                            elif self.display.pixel_array[xcoordinate,ycoordinate] == 0 and bit == 1:
                                self.display.pixel_array[xcoordinate,ycoordinate] = (255,255,255)
                        xcoordinate+=1
            ycoordinate+=1
            xcoordinate = x_access
        pygame.display.flip()

rom_path = os.path.join(os.getcwd(), "roms", "Pong (1 player).ch8")
c8 = chip8(rom_path, False)
c8.startgame()