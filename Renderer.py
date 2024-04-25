import os
import time
from sys import exit
import numpy as np
import pyautogui as pag
import pygame as pg
import win32api
import win32con

"""
CONTROLS:
Camera Movement: WASD
Camera Rotation: mouse
"""

# pygame settings
dims = (1080, 720)
window_pos = ((1920-dims[0])/2, (1080-dims[1])/2)
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % window_pos
mouse_pos = (0, 0)

pg.init()
stime = time.time()
clock = pg.time.Clock()

screen = pg.display.set_mode(dims)

models = []


class Model:
    def __init__(self, center, verts,  lines, scale=1, vcols=None, ecols=None):
        if vcols is None:
            vcols = {}
        if ecols is None:
            ecols = {}
        self.center = center
        self.vertices = [sm(scale, vert) for vert in verts]
        self.edges = lines  # contains the indexes of the vertices in the that share an edge

        self.vert_colors = vcols    # color of the points
        self.edge_colors = ecols    # color of the edges

        models.append(self)

    def move_obj_to(self, pos):
        self.center = pos

    def rot_obj(self, angle, axix=(0, 0, 1)):
        self.vertices = [rot_vec(vertex, angle, axix) for vertex in self.vertices]


class Camera:
    def __init__(self, pos, mouse_control=True):
        self.pos = pos
        self.right = (1, 0, 0)
        self.up = (0, 1, 0)
        self.dir = (0, 0, 1)
        self.fov = 80  # horizontal field-of-view angle in degrees
        self.viewplane_dis = 50  # distance of the viewplane relative to the camera
        self.speed = 5
        self.rot_speed = .05
        self.mouse_control = mouse_control

    def display_verts(self, obj):
        for vertex_index in range(len(obj.vertices)):
            try:
                color = obj.vert_colors[vertex_index]
            except KeyError:
                color = "White"
            drawpoint(self.project_to_screen(va(obj.center, obj.vertices[vertex_index])), color)

    def display_edges(self, obj):
        for edge_index in range(len(obj.edges)):
            try:
                color = obj.edge_colors[edge_index]
            except KeyError:
                color = "White"
            vert1 = va(obj.center, obj.vertices[obj.edges[edge_index][0]])
            vert2 = va(obj.center, obj.vertices[obj.edges[edge_index][1]])
            drawline(self.project_to_screen(vert1), self.project_to_screen(vert2), color)

    def project_to_screen(self, point):
        # the location of the point, if you imagine the camera to be at the center of a coordinate system, always 
        # pointing in the y direction (it calculates the l-combination of the point to the cam-dir and its normalvector)
        # converts the cameravectors into a list so that they can be used in the linear-combination algorhythm
        cam_vecs = np.array([[self.right[i], self.up[i], self.dir[i]] for i in range(3)])
        cam_space_point = np.linalg.solve(cam_vecs, va(point, self.pos, sign=-1))

        cam_and_point_dot = np.dot(cam_space_point, (0, 0, 1))
        point_angle = np.arccos(cam_and_point_dot / (magn(cam_space_point)))

        if point_angle < np.pi / 2:  # checks if the point is visable
            stretch_factor = self.viewplane_dis / cam_and_point_dot
            cam_space_proj_point = sm(stretch_factor, cam_space_point)[:2]  # reduces the dimension of the points to 2D
            cam_space_proj_point = (cam_space_proj_point[0], -1 * cam_space_proj_point[1])  # flips image (pygame-BS)
            cam_space_proj_point = va(sm(7, cam_space_proj_point), sm(.5, dims))  # centers points on screen
            return cam_space_proj_point

    def move_cam(self):  # camera controller to move the camera around with the keyboard
        velocity = [0, 0, 0]
        rotation = [0, 0]  # only 2 values because the camera doesn't need to turn around the z axis
        key_list = pg.key.get_pressed()
        # movement forward/backward
        if key_list[pg.K_w]:
            velocity[2] = self.speed
        elif key_list[pg.K_s]:
            velocity[2] = -self.speed
        # movement right/left
        if key_list[pg.K_d]:
            velocity[0] = self.speed
        elif key_list[pg.K_a]:
            velocity[0] = -self.speed
        # movement up/down
        if key_list[pg.K_SPACE]:
            velocity[1] = self.speed
        elif key_list[pg.K_LSHIFT]:
            velocity[1] = -self.speed

        if self.mouse_control:
            rotation = sm(0.005, move_mouse())
        else:
            # rotation left/right
            if key_list[pg.K_LEFT]:
                rotation[1] = -self.rot_speed
            elif key_list[pg.K_RIGHT]:
                rotation[1] = self.rot_speed
            # rotation up/downright
            if key_list[pg.K_DOWN]:
                rotation[0] = -self.rot_speed
            elif key_list[pg.K_UP]:
                rotation[0] = self.rot_speed

        # apply x-axis rotation
        self.up, self.dir = rot_vec(self.up, rotation[0], self.right), rot_vec(self.dir, rotation[0], self.right)
        # apply y-axis rotation (rotation around the global y-axis so that it doesn't rotate around the z-axis
        self.right = rot_vec(self.right, rotation[1], (0, 1, 0))
        self.up = rot_vec(self.up, rotation[1], (0, 1, 0))
        self.dir = rot_vec(self.dir, rotation[1], (0, 1, 0))

        move_vec = va(sm(velocity[0], self.right), sm(velocity[1], self.up), sm(velocity[2], self.dir))
        self.pos = va(self.pos, move_vec)

    def draw_cam(self):  # displays the camera and its FOV legs to show its direction (only used in 2D)
        drawpoint(self.pos, "Yellow", 7)

        fov_leg1_vec = rot_vec(self.dir, np.deg2rad(self.fov / 2))
        fov_leg1_end = va(self.pos, sm(2000, fov_leg1_vec))
        drawline(self.pos, fov_leg1_end, "Yellow")

        fov_leg2_vec = rot_vec(self.dir, -np.deg2rad(self.fov / 2))
        fov_leg2_end = va(self.pos, sm(2000, fov_leg2_vec))
        drawline(self.pos, fov_leg2_end, "Yellow")


def move_mouse():
    global mouse_pos
    current_mouse_pos = pag.position()
    delta_mouse = va(mouse_pos, current_mouse_pos, sign=-1)[::-1]
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(window_center[0]/1920*65535.0),
                         int(window_center[1]/1080*65535.0))
    mouse_pos = current_mouse_pos
    return delta_mouse


def va(vector1, vector2, vector3=(0, 0, 0), sign=1):   # vector-addition (only use sign if adding 2 vectors)
    summed_vector = [vector1[i] + sign*vector2[i] + vector3[i] for i in range(len(vector1))]
    return summed_vector


def sm(scalar, vector):     # scalar-multiplication of a vector
    scaled_vector = [scalar * element for element in vector]
    return scaled_vector


def magn(vector):   # get the magnitude of a vector
    magnitude = (np.sum([element**2 for element in vector])) ** 0.5
    return magnitude


def rot_vec(vector, angle, axis=(0, 1, 0)):     # rotate a vector around the axis, angle in radians
    axis = sm(1/magn(axis), axis)
    dot = np.dot(axis, vector)
    cos = np.cos(angle)
    sin = np.sin(angle)
    new_vector = va(sm(dot*(1-cos), axis), sm(cos, vector), sm(sin, np.cross(axis, vector)))
    return new_vector


def drawline(start, end, color="White", width=3):
    if start and end:
        pg.draw.line(screen, color, start, end, width)


def drawpoint(position, color="White", size=5):
    if position:    # allows for no position to be given
        pg.draw.circle(screen, color, position, size)


cam = Camera((0, 0, 100))

Cube = Model((0, 0, 300),
             [(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
              (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)],
             [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 5), (2, 6), (3, 7), (4, 5), (5, 6), (6, 7), (7, 4)],
             100)

window_center = va(window_pos, sm(0.5, dims))   # center of the window in screen coordinates
move_mouse()

while True:     # main loop in which everything happens
    for event in pg.event.get():
        if event.type == pg.QUIT or pg.key.get_pressed()[pg.K_ESCAPE]:
            pg.quit()
            exit()
    if not pg.mouse.get_focused():
        pg.mouse.set_visible(True)
        continue
    pg.mouse.set_visible(False)

    screen.fill("Black")

    move_mouse()
    cam.move_cam()

    for model in models:
        cam.display_edges(model)
        cam.display_verts(model)

    pg.display.update()
    # print(1/-(stime - (stime := time.time())))  # show fps
    clock.tick(60)
