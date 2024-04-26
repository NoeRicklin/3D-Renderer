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
window_pos = ((1920 - dims[0]) / 2, (1080 - dims[1]) / 2)
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % window_pos
mouse_pos = (0, 0)

pg.init()
stime = time.time()
clock = pg.time.Clock()

screen = pg.display.set_mode(dims)

models = []


class Model:
    def __init__(self, center, vertices, triangles, scale=1, trg_colors={}):
        self.center = center
        self.vertices = [sm(scale, vertex) for vertex in vertices]
        self.triangles = []
        for index, triangle in enumerate(triangles):
            trg_verts = [self.vertices[index] for index in triangle]
            try:
                trg_col = trg_colors[index]
                self.triangles.append(Triangle(trg_verts, trg_col))
            except KeyError:
                self.triangles.append(Triangle(trg_verts))

        models.append(self)

    def order_triangles(self):
        self.triangles = sorted(self.triangles, key=lambda triangle: magn(va(cam.pos, va(self.center, triangle.center), sign=-1)), reverse=True)

    def get_trg_center(self, triangle):
        points = [self.vertices[triangle[i]] for i in range(3)]
        points_x = [points[i][0] for i in range(3)]
        points_y = [points[i][1] for i in range(3)]
        points_z = [points[i][2] for i in range(3)]

        center_x = (min(points_x) + (max(points_x) - min(points_x)) / 2)
        center_y = (min(points_y) + (max(points_y) - min(points_y)) / 2)
        center_z = (min(points_z) + (max(points_z) - min(points_z)) / 2)
        return center_x, center_y, center_z

    def move_obj_to(self, pos):
        self.center = pos

    def rot_obj(self, angle, axix=(0, 0, 1)):
        self.vertices = [rot_vec(vertex, angle, axix) for vertex in self.vertices]


class Triangle:
    def __init__(self, vertices, color="White"):
        self.vertices = vertices
        self.center = self.get_center()
        self.color = color

    def get_center(self):
        points_x = [self.vertices[i][0] for i in range(3)]
        points_y = [self.vertices[i][1] for i in range(3)]
        points_z = [self.vertices[i][2] for i in range(3)]

        center_x = (min(points_x) + (max(points_x) - min(points_x)) / 2)
        center_y = (min(points_y) + (max(points_y) - min(points_y)) / 2)
        center_z = (min(points_z) + (max(points_z) - min(points_z)) / 2)
        return center_x, center_y, center_z


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
                color = obj.vertex_colors[vertex_index]
            except KeyError:
                color = "White"
            drawpoint(self.project_to_screen(va(obj.center, obj.vertices[vertex_index])), color)

    def display_triangles(self, obj):
        for triangle in obj.triangles:
            vert1 = self.project_to_screen(va(obj.center, triangle.vertices[0]))
            vert2 = self.project_to_screen(va(obj.center, triangle.vertices[1]))
            vert3 = self.project_to_screen(va(obj.center, triangle.vertices[2]))
            drawtriangle(vert1, vert2, vert3, triangle.color)

    def project_to_screen(self, point):
        # the location of the point, if you imagine the camera to be at the center of a coordinate system, always 
        # pointing in the y direction (it calculates the l-combination of the point to the cam-dir and its normalvector)
        # converts the cameravectors into a list so that they can be used in the linear-combination algorhythm
        cam_vecs = np.array([[self.right[i], self.up[i], self.dir[i]] for i in range(3)])
        cam_space_point = np.linalg.solve(cam_vecs, va(point, self.pos, sign=-1))

        cam_and_point_dot = np.dot(cam_space_point, (0, 0, 1))

        if cam_and_point_dot > 0:  # checks if the point is visable
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
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE,
                         int(window_center[0] / 1920 * 65535.0),
                         int(window_center[1] / 1080 * 65535.0))
    mouse_pos = current_mouse_pos
    return delta_mouse


def va(vector1, vector2, vector3=(0, 0, 0), sign=1):  # vector-addition (only use sign if adding 2 vectors)
    summed_vector = [vector1[i] + sign * vector2[i] + vector3[i] for i in range(len(vector1))]
    return summed_vector


def sm(scalar, vector):  # scalar-multiplication of a vector
    scaled_vector = [scalar * element for element in vector]
    return scaled_vector


def magn(vector):  # get the magnitude of a vector
    magnitude = (np.sum([element ** 2 for element in vector])) ** 0.5
    return magnitude


def rot_vec(vector, angle, axis=(0, 1, 0)):  # rotate a vector around the axis, angle in radians
    axis = sm(1 / magn(axis), axis)
    dot = np.dot(axis, vector)
    cos = np.cos(angle)
    sin = np.sin(angle)
    new_vector = va(sm(dot * (1 - cos), axis), sm(cos, vector), sm(sin, np.cross(axis, vector)))
    return new_vector


def drawpoint(position, color="White", size=5):
    if position:  # allows for no position to be given
        pg.draw.circle(screen, color, position, size)


def drawline(start, end, color="White", width=3):
    if start and end:
        pg.draw.line(screen, color, start, end, width)


def drawtriangle(p1, p2, p3, color="White"):
    if p1 and p2 and p3:
        pg.draw.polygon(screen, color, (p1, p2, p3))


cam = Camera((0, 0, 100))

Cube = Model((0, 0, 300),
             [(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
              (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)],
             # triangle-vertices must go clockwise when looked at from outside the model
             [(0, 3, 1), (3, 2, 1), (3, 7, 2), (7, 6, 2), (4, 6, 7), (4, 5, 6), (0, 5, 4), (0, 1, 5),
              (4, 7, 0), (7, 3, 0), (1, 2, 5), (2, 6, 5)],
             100,
             {0: "Blue", 4: "Red", 10: "Green"})

window_center = va(window_pos, sm(0.5, dims))  # center of the window in screen coordinates
move_mouse()

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

    move_mouse()
    cam.move_cam()

    for model in models:
        model.order_triangles()
        cam.display_triangles(model)
        # cam.display_verts(model)

    pg.display.update()
    # print(1/-(stime - (stime := time.time())))  # show fps
    clock.tick(60)
