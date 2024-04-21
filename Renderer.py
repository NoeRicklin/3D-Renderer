import pygame as pg
from sys import exit
import numpy as np

# pygame settings
pg.init()
clock = pg.time.Clock()

dims = 1080, 720
screen = pg.display.set_mode(dims)


# camera settings
cam_pos = (0, 0, 0)
cam_dir = (0, 0, -1)
cam_fov = 80    # horizontal field-of-view angle in degrees
viewplane_dis = 50  # distance of the viewplane relative to the camera

speed = 5
rot_speed = .05

vertices = [(-50, -50, -300), (50, -50, -300), (50, 50, -300), (-50, 50, -300),
            (-50, -50, -400), (50, -50, -400), (50, 50, -400), (-50, 50, -400)]
vert_colors = {1: "Blue"}
edges = [(0, 1), (1, 2), (2, 3), (3, 0),
         (0, 4), (1, 5), (2, 6), (3, 7),
         (4, 5), (5, 6), (6, 7), (7, 4)]  # contains the indexes of the vertices in the that share an edge


def move_cam(current_pos, current_dir):     # camera controller to move the camera around with the keyboard
    velocity = 0
    rotation = 0

    key_list = pg.key.get_pressed()
    if key_list[pg.K_w]:
        velocity = speed
    elif key_list[pg.K_s]:
        velocity = -speed
    if key_list[pg.K_a]:
        rotation = rot_speed
    elif key_list[pg.K_d]:
        rotation = -rot_speed

    cam_dir_new = rot_vec(current_dir, rotation)
    cam_pos_new = va(current_pos, sm(velocity, cam_dir_new))
    return cam_pos_new, cam_dir_new


def draw_cam():     # displays the camera and its FOV legs to show its direction
    drawpoint(cam_pos, "Yellow", 7)

    fov_leg1_vec = rot_vec(cam_dir, np.deg2rad(cam_fov/2))
    fov_leg1_end = va(cam_pos, sm(2000, fov_leg1_vec))
    drawline(cam_pos, fov_leg1_end, "Yellow")

    fov_leg2_vec = rot_vec(cam_dir, -np.deg2rad(cam_fov / 2))
    fov_leg2_end = va(cam_pos, sm(2000, fov_leg2_vec))
    drawline(cam_pos, fov_leg2_end, "Yellow")


def project_to_screen(point):
    # the location of the point, if you imagine the camera to be at the center of a coordinate system, always pointing
    # in the y direction (it calculates the linear-combination of the point to the cam-dir and its normalvector)
    cam_right = rot_vec(cam_dir, -np.pi/2, "y")
    cam_up = (0, 1, 0)
    cam_space_point = tuple(np.linalg.solve([cam_right, cam_up, cam_dir], va(point, cam_pos, -1)))

    cam_and_point_dot = np.dot(cam_space_point, (0, 0, 1))
    point_angle = np.arccos(cam_and_point_dot / (magn(cam_space_point)))

    if point_angle < np.pi/2:   # checks if the point is visable
        stretch_factor = viewplane_dis / cam_and_point_dot
        cam_space_proj_point = sm(stretch_factor, cam_space_point)[:2]  # reduces the dimension of the points to 2D
        cam_space_proj_point = (cam_space_proj_point[0], -1*cam_space_proj_point[1])     # flips image because of pygame
        screen_scaler = dims[0] / (2*viewplane_dis*np.tan(cam_fov))
        print(screen_scaler)
        cam_space_proj_point = va(sm(7, cam_space_proj_point), sm(.5, dims))    # centers points on screen
        return cam_space_proj_point


def display_verts(show_global_vert=False):
    for vertex_index in range(len(vertices)):
        try:
            color = vert_colors[vertex_index]
        except KeyError:
            color = "White"
        if show_global_vert:
            drawpoint(vertices[vertex_index], color)
        drawpoint(project_to_screen(vertices[vertex_index]), color)


def display_edges(show_global_edge=False):
    for edge in edges:
        vert1, vert2 = vertices[edge[0]], vertices[edge[1]]
        if show_global_edge:
            drawline(vert1, vert2)
        drawline(project_to_screen(vert1), project_to_screen(vert2))


def va(vector1, vector2, sign=1):   # vector-addition
    summed_vector = [vector1[i] + sign*vector2[i] for i in range(len(vector1))]
    return summed_vector


def sm(scalar, vector):     # scalar-multiplication of a vector
    scaled_vector = [scalar * element for element in vector]
    return scaled_vector


def magn(vector):   # get the magnitude of a vector
    magnitude = (np.sum([element**2 for element in vector])) ** 0.5
    return magnitude


def rot_vec(vector, angle, axis="y"):     # rotate a vector, angle in radians
    rot_mat = [[1, 0, 0],
               [0, 1, 0],
               [0, 0, 1]]
    if axis == "x":
        rot_mat = [[1, 0, 0],
                   [0, np.cos(angle), -np.sin(angle)],
                   [0, np.sin(angle), np.cos(angle)]]
    elif axis == "y":
        rot_mat = [[np.cos(angle), 0, np.sin(angle)],
                   [0, 1, 0],
                   [-np.sin(angle), 0, np.cos(angle)]]
    elif axis == "z":
        rot_mat = [[np.cos(angle), -np.sin(angle), 0],
                   [np.sin(angle), np.cos(angle), 0],
                   [0, 0, 1]]

    new_vector = np.matmul(rot_mat, vector)
    return new_vector


def drawline(start, end, color="White", width=3):
    if start and end:
        pg.draw.line(screen, color, start, end, width)


def drawpoint(position, color="White", size=5):
    if position:    # allows for no position to be given
        pg.draw.circle(screen, color, position, size)


while True:     # main loop in which everything happens
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
    screen.fill("Black")

    cam_pos, cam_dir = move_cam(cam_pos, cam_dir)

    display_edges()
    display_verts()

    pg.display.update()
    clock.tick(60)
