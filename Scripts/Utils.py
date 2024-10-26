import numpy as np
import pygame as pg
import pyautogui as pag
import win32api, win32con
from sys import exit
import time

stime = time.time()
dtime = 0
clock = pg.time.Clock()


def va(vector1, vector2, vector3=(0, 0, 0), sign=1):  # vector-addition (only use sign if adding 2 vectors)
    summed_vector = [vector1[i] + sign * vector2[i] + vector3[i] for i in range(len(vector1))]
    return summed_vector


def sm(scalar, vector):  # scalar-multiplication of a vector
    scaled_vector = [scalar * element for element in vector]
    return scaled_vector


def dot(vector1, vector2):  # dot product of two vectors
    component_multiplied = [vector1[i] * vector2[i] for i in range(len(vector1))]
    dot_product = sum(component_multiplied)
    return dot_product


def magn(vector):  # get the magnitude of a vector
    magnitude = (np.sum([element ** 2 for element in vector])) ** 0.5
    return magnitude


def clamp(value, output_range):
    clamped_value = max(output_range[0], min(output_range[1], value))
    return clamped_value


def norm(vector):  # get the normalized vector
    norm_vec = sm(1 / magn(vector), vector)
    return norm_vec


def rot_vec(vector, angle, axis=(0, 1, 0)):  # rotate a vector around the axis, angle in radians
    axis = norm(axis)
    dot = np.dot(axis, vector)
    cos = np.cos(angle)
    sin = np.sin(angle)
    new_vector = va(sm(dot * (1 - cos), axis), sm(cos, vector), sm(sin, np.cross(axis, vector)))
    return new_vector


def modelfile2object(path):
    file = open(path)
    lines_str = file.read().split("\n")

    vertices = []
    triangles = []
    for line in lines_str:
        if len(line) < 2:
            continue
        if line[0:2] == "v ":
            vertex = [float(number) for number in line[2::].split(" ")]
            vertices.append(vertex)
        if line[0:2] == "f ":
            triangle = [int(index.split("/")[0]) - 1 for index in line[2::].split(" ")[:3]]
            triangles.append(triangle)
    file.close()
    return vertices, triangles


def event_checks():
    for event in pg.event.get():
        if event.type == pg.QUIT or pg.key.get_pressed()[pg.K_ESCAPE]:
            pg.quit()
            exit()


def get_mouse_movement():
    import Scene_Setup  # needs to import Scene_Setup as a whole to redefine its mouse_pos var
    current_mouse_pos = pag.position()
    delta_mouse = va(Scene_Setup.mouse_pos, current_mouse_pos, sign=-1)[::-1]
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE,
                         int(Scene_Setup.window_center[0] / 1920 * 65535.0),
                         int(Scene_Setup.window_center[1] / 1080 * 65535.0))
    Scene_Setup.mouse_pos = current_mouse_pos
    return delta_mouse


def drawpoint(position, color="White", size=4):
    from Scene_Setup import screen
    if position:  # allows for no position to be given
        pg.draw.circle(screen, color, position, size)


def drawline(start, end, color="White", width=2):
    from Scene_Setup import screen
    if start and end:
        pg.draw.line(screen, color, start, end, width)


def print_fps():
    import Scene_Setup as ss
    global dtime, stime
    if ss.show_fps:
        dtime = -(stime - (time.time()))
        stime = time.time()
        try:
            print(f"{round(1 / dtime, 2)} FPS")
        except ZeroDivisionError:
            print(f"1042.37 FPS")
