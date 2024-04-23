import pygame as pg
from sys import exit
import numpy as np

# pygame settings
pg.init()
clock = pg.time.Clock()

dims = 1080, 720
screen = pg.display.set_mode(dims)

# camera settings
cam_pos = (0, 0, 100)
cam_dir = (0, 0, 1)
cam_fov = 80    # horizontal field-of-view angle in degrees
viewplane_dis = 50  # distance of the viewplane relative to the camera

speed = 5
rot_speed = .05

# vertices settings
vertices = [(-50, -50, 300), (50, -50, 300), (50, 50, 300), (-50, 50, 300),
            (-50, -50, 400), (50, -50, 400), (50, 50, 400), (-50, 50, 400)]
vert_colors = {1: "Blue"}

edges = [(0, 1), (1, 2), (2, 3), (3, 0),
         (0, 4), (1, 5), (2, 6), (3, 7),
         (4, 5), (5, 6), (6, 7), (7, 4)]  # contains the indexes of the vertices in the that share an edge
edge_colors = {2: "Blue"}


def move_cam(current_pos, current_dir):     # camera controller to move the camera around with the keyboard
    velocity = [0, 0, 0]
    rotation = 0

    key_list = pg.key.get_pressed()
    # movement forward/backward
    if key_list[pg.K_w]:
        velocity[2] = speed
    elif key_list[pg.K_s]:
        velocity[2] = -speed
    # movement right/left
    if key_list[pg.K_d]:
        velocity[0] = speed
    elif key_list[pg.K_a]:
        velocity[0] = -speed
    # movement up/down
    if key_list[pg.K_SPACE]:
        velocity[1] = speed
    elif key_list[pg.K_LSHIFT]:
        velocity[1] = -speed

    # rotation left/right
    if key_list[pg.K_LEFT]:
        rotation = -rot_speed
    elif key_list[pg.K_RIGHT]:
        rotation = rot_speed

    cam_dir_new = rot_vec(current_dir, rotation)
    cam_right_new = rot_vec(cam_dir_new, np.pi / 2, "y")
    cam_up_new = (0, 1, 0)

    move_vec = va(sm(velocity[0], cam_right_new), sm(velocity[1], cam_up_new), sm(velocity[2], cam_dir_new))
    cam_pos_new = va(current_pos, move_vec)
    return cam_pos_new, cam_dir_new


def draw_cam():     # displays the camera and its FOV legs to show its direction (only used in 2D)
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
    cam_right = rot_vec(cam_dir, np.pi/2, "y")
    cam_up = (0, 1, 0)

    # converts the cameravectors into a list so that they can be used in the linear-combination algorhythm
    cam_vecs = np.array([[cam_right[i], cam_up[i], cam_dir[i]] for i in range(3)])
    cam_space_point = np.linalg.solve(cam_vecs, va(point, cam_pos, sign=-1))

    cam_and_point_dot = np.dot(cam_space_point, (0, 0, 1))
    point_angle = np.arccos(cam_and_point_dot / (magn(cam_space_point)))

    if point_angle < np.pi/2:   # checks if the point is visable
        stretch_factor = viewplane_dis / cam_and_point_dot
        cam_space_proj_point = sm(stretch_factor, cam_space_point)[:2]  # reduces the dimension of the points to 2D
        cam_space_proj_point = (cam_space_proj_point[0], -1*cam_space_proj_point[1])     # flips image because of pygame
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
    for edge_index in range(len(edges)):
        try:
            color = edge_colors[edge_index]
        except KeyError:
            color = "White"
        vert1, vert2 = vertices[edges[edge_index][0]], vertices[edges[edge_index][1]]
        if show_global_edge:
            drawline(vert1, vert2, color)
        drawline(project_to_screen(vert1), project_to_screen(vert2), color)


def va(vector1, vector2, vector3=(0, 0, 0), sign=1):   # vector-addition (only use sign if adding 2 vectors)
    summed_vector = [vector1[i] + sign*vector2[i] + vector3[i] for i in range(len(vector1))]
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
