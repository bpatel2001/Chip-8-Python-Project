import pygame

pygame.init()

SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
run = True

#Create memory
memory = [0] * 4096
registers = [0] * 16
pc = 0x200
I = 0

f = open("E:/CHIP-8/roms/test_opcode.ch8", "rb")

#Allocating font
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
    memory[i] = font[fontpos]
    fontpos+=1

#Putting rom into memory starting from 0x200
for i in range(0x200, len(memory)):
    byte = f.read(1)
    if not byte:
        break
    memory[i] = int.from_bytes(byte, byteorder='big')

print(memory)

#Combine opcodes and then append PC by 2

def fetchopcode(memory, pc):
    opcode = memory[pc] << 8 | memory[pc+1]
    pc+=2
    return opcode, pc

def executeopcode(opcode):
    n1 = opcode & 0xF000
    n2 = opcode & 0x0F00
    n3 = opcode & 0x00F0
    n4 = opcode & 0x000F

    #Clear display (00E0)
    if opcode == 0x00E0:
        screen.fill((0,0,0))
        pygame.display.flip()
    
    #Make PC jump to NNN position (1XNN)
    elif n1 == 0x1000:
        jump_pos = n2 + n3 + n4
        pc = jump_pos

    #Change register value at x position (6XNN)
    elif n1 == 0x6000:
        value = n3 + n4
        pos = n2 >> 8
        registers[pos] = value

    #Add register value at x position (7XNN)
    elif n1 == 0x7000:
        value = n3 + n4
        pos = n2 >> 8
        registers[pos] += value

    #Set index register I (AXNNN)
    elif n1 == 0xA000:
        value = n2 + n3 + n4
        I = value

        



while run:

    screen.fill((0,0,0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()