import pygame as pg
import os
from sys import exit

from Utils import *

dims = (1600, 900)

pg.init()
screen = pg.display.set_mode(dims)


def drawpoint(position, color="White", size=3):
    if position:  # allows for no position to be given
        screen.set_at(position, color)


def calc_line(start, end, color="White", size=1):
    line_points = []

    start, end = sorted([start, end], key=lambda x: x[0])
    if abs(end[0] - start[0]) >= abs(end[1] - start[1]):  # if slope >= 1
        slope = (end[1] - start[1]) / (end[0] - start[0])
        for pixel_index in range(end[0] - start[0] + 1):
            pixel_height = round(slope * pixel_index)

            pixel_pos = (start[0] + pixel_index, start[1] + pixel_height)
            line_points.append(pixel_pos)
            # screen.set_at(pixel_pos, "White")
    else:   # if slope > 1
        start, end = sorted([start, end], key=lambda x: x[1])
        slope = (start[0] - end[0]) / (end[1] - start[1])
        for pixel_index in range(end[1]-start[1] + 1):
            pixel_height = round(slope * pixel_index)

            pixel_pos = (start[0] - pixel_height, start[1] + pixel_index)
            line_points.append(pixel_pos)
            # screen.set_at(pixel_pos, "White")
    return line_points


p1 = (500, 450)
p2 = (900, 300)
p3 = (700, 600)


while True:  # main loop in which everything happens
    for event in pg.event.get():
        if event.type == pg.QUIT or pg.key.get_pressed()[pg.K_ESCAPE]:
            pg.quit()
            exit()

    if not pg.mouse.get_focused():
        pg.mouse.set_visible(True)
        continue
    pg.mouse.set_visible(False)

    screen.fill("Black")

    line_points = sorted(calc_line(p2, p1)+calc_line(p3, p1)+calc_line(p3, p2), key=lambda x: x[0])
    trg_length = line_points[-1][0] - line_points[0][0]
    for row_index in range(trg_length):
        row_points = []
        first_row_point_index = 0
        while line_points[first_row_point_index][0] != row_index + line_points[0][0]:
            first_row_point_index += 1
        last_row_point_index = first_row_point_index
        while (point := line_points[last_row_point_index])[0] == row_index + line_points[0][0]:
            row_points.append(point)
            last_row_point_index += 1
        row_height_range = min([i[1] for i in row_points]), max([i[1] for i in row_points])
        for height in range(row_height_range[0], row_height_range[1]):
            pixel_pos = (row_index + line_points[0][0], height)
            screen.set_at(pixel_pos, "White")
        if row_height_range[1]-row_height_range[0] == 0:
            print(row_index)

    # calc_line(p3, p1)

    # screen.set_at(p1, "Red")
    # screen.set_at(p2, "Red")
    # screen.set_at(p3, "Red")


    # pg.draw.polygon(screen, "Yellow", (p1, p2, p3))

    pg.display.update()
