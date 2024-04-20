import pygame as pg
from sys import exit
import numpy as np

pg.init()
clock = pg.time.Clock()

WIDTH, HEIGHT = 1024, 720
screen = pg.display.set_mode((WIDTH, HEIGHT))


def va(vector1, vector2, sign=1):   # vector-addition
    summed_vector = [vector1[i] + vector2[i] for i in range(len(vector1))]
    return summed_vector


def sm(scalar, vector):     # scalar-multiplication of a vector
    scaled_vector = [scalar * element for element in vector]
    return scaled_vector


def drawline(start, end, color="White", width=2):
    pg.draw.line(screen, color, start, end, width)


def drawpoint(position, color="White", size=4):
    pg.draw.circle(screen, color, position, size)


while True:     # main loop in which everything happens
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
    screen.fill("Black")

    pg.display.update()
    clock.tick(60)
