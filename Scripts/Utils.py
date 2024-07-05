import numpy as np
import pygame as pg
import pyautogui as pag
import win32api
import win32con
from sys import exit
import time


def va(vector1, vector2, vector3=(0, 0, 0), sign=1):  # vector-addition (only use sign if adding 2 vectors)
    summed_vector = [vector1[i] + sign * vector2[i] + vector3[i] for i in range(len(vector1))]
    return summed_vector


def sm(scalar, vector):  # scalar-multiplication of a vector
    scaled_vector = [scalar * element for element in vector]
    return scaled_vector


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


def convert_obj_file(path):
    file = open(path)
    lines_str = file.read().split("\n")

    vertices = []
    triangles = []
    for line in lines_str:
        try:
            if line[0:2] == "v ":
                vertex = [float(number) for number in line[2::].split(" ")]
                vertices.append(vertex)
            if line[0:2] == "f ":
                triangle = [int(index) - 1 for index in line[2::].split(" ")]
                triangles.append(triangle)
        except IndexError:
            continue
    file.close()
    return vertices, triangles


def running_checks():
    for event in pg.event.get():
        if event.type == pg.QUIT or pg.key.get_pressed()[pg.K_ESCAPE]:
            pg.quit()
            exit()


def get_mouse_movement():
    import Scene_Setup
    current_mouse_pos = pag.position()
    delta_mouse = va(Scene_Setup.mouse_pos, current_mouse_pos, sign=-1)[::-1]
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE,
                         int(Scene_Setup.window_center[0] / 1920 * 65535.0),
                         int(Scene_Setup.window_center[1] / 1080 * 65535.0))
    Scene_Setup.mouse_pos = current_mouse_pos
    return delta_mouse


def drawpoint(position, color="White", size=5):
    from Scene_Setup import screen
    if position:  # allows for no position to be given
        pg.draw.circle(screen, color, position, size)


def drawline(start, end, color="White", width=1):
    from Scene_Setup import screen
    if start and end:
        pg.draw.line(screen, color, start, end, width)


def calc_fps():
    import Scene_Setup
    Scene_Setup.dtime = -(Scene_Setup.stime - (time.time()))
    Scene_Setup.stime = time.time()
    try:
        return f"{round(1 / Scene_Setup.dtime, 2)} FPS"
    except ZeroDivisionError:
        return "n/a"
