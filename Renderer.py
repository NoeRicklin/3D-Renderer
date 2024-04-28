import os
from sys import exit
import pygame as pg
import numpy as np
import time
import pyautogui as pag
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

light_source_dir = (0, 200, -500)
environment_light_percent = 0.3  # amount of illumination in spots without direct lighting (value between 0 and 1)

pg.init()
screen = pg.display.set_mode(dims)

stime = time.time()
dtime = 0
clock = pg.time.Clock()

models = []


class Model:
    def __init__(self, center, vertices, triangles, color=(255, 255, 255), scale=1):
        self.center = center
        self.vertices = [sm(scale, vertex) for vertex in vertices]
        self.color = color
        self.triangles = []
        for triangle in triangles:
            self.triangles.append(Triangle(self, triangle, color))

        models.append(self)

    def order_triangles(self, cam):
        self.triangles.sort(key=lambda trg: magn(va(cam.pos, va(self.center, trg.center), sign=-1)), reverse=True)

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

    def rot_obj(self, angle, axis=(0, 0, 1)):
        self.vertices = [rot_vec(vertex, angle, axis) for vertex in self.vertices]
        for trg_index in range(len(self.triangles)):
            self.triangles[trg_index].center = rot_vec(self.triangles[trg_index].center, angle, axis)
            self.triangles[trg_index].normal = rot_vec(self.triangles[trg_index].normal, angle, axis)
            self.triangles[trg_index].color = self.triangles[trg_index].calc_brightness((255, 0, 0))


class Triangle:
    def __init__(self, parent, vertices, color=(255, 255, 255)):
        self.vertices = vertices
        self.parent = parent
        self.center = self.get_center()
        self.normal = self.get_normal()
        self.color = self.calc_brightness(color)

    def get_center(self):
        points_x = [self.parent.vertices[self.vertices[i]][0] for i in range(3)]
        points_y = [self.parent.vertices[self.vertices[i]][1] for i in range(3)]
        points_z = [self.parent.vertices[self.vertices[i]][2] for i in range(3)]

        center_x = (min(points_x) + (max(points_x) - min(points_x)) / 2)
        center_y = (min(points_y) + (max(points_y) - min(points_y)) / 2)
        center_z = (min(points_z) + (max(points_z) - min(points_z)) / 2)
        return center_x, center_y, center_z

    def get_normal(self):  # vertices are assumed to be defined in clockwise-order when looked at from outside
        v1 = va(self.parent.vertices[self.vertices[1]], self.parent.vertices[self.vertices[0]], sign=-1)
        v2 = va(self.parent.vertices[self.vertices[2]], self.parent.vertices[self.vertices[1]], sign=-1)
        normal_vector = norm(np.cross(v1, v2))
        return normal_vector

    def calc_brightness(self, max_col):
        clamped_dot = max(0, np.dot(self.normal, light_source_dir))
        return pg.Color(sm(environment_light_percent + clamped_dot - environment_light_percent*clamped_dot, max_col))


class Camera:
    def __init__(self, pos, mouse_control=True):
        self.pos = pos
        self.right = (1, 0, 0)
        self.up = (0, 1, 0)
        self.dir = (0, 0, 1)
        self.fov = 80  # horizontal field-of-view angle in degrees
        self.viewplane_dis = 50  # distance of the viewplane relative to the camera
        self.speed = 1000
        self.rot_speed = .4
        self.mouse_control = mouse_control

    def display_verts(self, obj):
        for vertex_index in range(len(obj.vertices)):
            try:
                color = obj.vertex_colors[vertex_index]
            except KeyError:
                color = "White"
            drawpoint(self.project_to_screen(va(obj.center, obj.vertices[vertex_index])), color)

    def display_triangles(self, obj):
        obj.order_triangles(self)
        for triangle in obj.triangles:
            vert1 = self.project_to_screen(va(obj.center, obj.vertices[triangle.vertices[0]]))
            vert2 = self.project_to_screen(va(obj.center, obj.vertices[triangle.vertices[1]]))
            vert3 = self.project_to_screen(va(obj.center, obj.vertices[triangle.vertices[2]]))
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
            rotation = sm(self.rot_speed, move_mouse())
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

        velocity = sm(dtime, velocity)
        rotation = sm(dtime, rotation)

        self.rot_cam(rotation)
        move_vec = va(sm(velocity[0], self.right), sm(velocity[1], self.up), sm(velocity[2], self.dir))
        self.pos = va(self.pos, move_vec)

    def rot_cam(self, rotation):
        # apply x-axis rotation
        self.up, self.dir = rot_vec(self.up, rotation[0], self.right), rot_vec(self.dir, rotation[0], self.right)
        # apply y-axis rotation (rotation around the global y-axis so that it doesn't rotate around the z-axis
        self.right = rot_vec(self.right, rotation[1], (0, 1, 0))
        self.up = rot_vec(self.up, rotation[1], (0, 1, 0))
        self.dir = rot_vec(self.dir, rotation[1], (0, 1, 0))

    def draw_cam(self):  # displays the camera and its FOV legs to show its direction (only used in 2D)
        drawpoint(self.pos, "Yellow", 7)

        fov_leg1_vec = rot_vec(self.dir, np.deg2rad(self.fov / 2))
        fov_leg1_end = va(self.pos, sm(2000, fov_leg1_vec))
        drawline(self.pos, fov_leg1_end, "Yellow")

        fov_leg2_vec = rot_vec(self.dir, -np.deg2rad(self.fov / 2))
        fov_leg2_end = va(self.pos, sm(2000, fov_leg2_vec))
        drawline(self.pos, fov_leg2_end, "Yellow")


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
                triangle = [int(index)-1 for index in line[2::].split(" ")]
                triangles.append(triangle)
        except:
            continue
    file.close()
    return vertices, triangles


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


def norm(vector):  # get the normalized vector
    norm_vec = sm(1/magn(vector), vector)
    return norm_vec


def rot_vec(vector, angle, axis=(0, 1, 0)):  # rotate a vector around the axis, angle in radians
    axis = norm(axis)
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


def drawtriangle(p1, p2, p3, color):
    if p1 and p2 and p3:
        pg.draw.polygon(screen, color, (p1, p2, p3))


light_source_dir = norm(light_source_dir)

cam = Camera((0, 0, 0))

# Cube = Model((0, 0, 300),
#              [(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
#               (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)],
#              # triangle-vertices must go clockwise when looked at from outside the model
#              [(0, 3, 1), (3, 2, 1), (3, 7, 2), (7, 6, 2), (4, 6, 7), (4, 5, 6), (0, 5, 4), (0, 1, 5),
#               (4, 7, 0), (7, 3, 0), (1, 2, 5), (2, 6, 5)],
#              (255, 255, 255),
#              scale=100)
# models.append(Cube))

vertices, triangles = convert_obj_file("Models/VideoShip.obj")
Plane = Model((0, -300, 1000), vertices, triangles, (255, 0, 0), 100)
Plane.rot_obj(np.pi, (0, 1, 0))

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
        cam.display_triangles(model)
        # cam.display_verts(model)

    pg.display.update()
    dtime = -(stime - (stime := time.time()))
    # print(1/dtime)  # show fps
    clock.tick(60)
