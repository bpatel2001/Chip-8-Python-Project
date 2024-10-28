import pygame

SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pixel_array = pygame.PixelArray(screen)

pygame.init()

run = True

while run:

    pixel_array[0,0] = (255,255,255)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()


