import pygame as pg
from sys import exit
import numpy as np

pg.init()
clock = pg.time.Clock()

WIDTH, HEIGHT = 1024, 720
screen = pg.display.set_mode((WIDTH, HEIGHT))


while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
    screen.fill("Black")

    pg.display.update()
    clock.tick(60)
