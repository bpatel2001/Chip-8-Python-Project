import pygame

class Screen:
    def __init__(self):
        self.SCREEN_WIDTH = 64
        self.SCREEN_HEIGHT = 32

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), flags = pygame.SCALED | pygame.RESIZABLE | pygame.FULLSCREEN)
        self.pixel_array = pygame.PixelArray(self.screen)


        

