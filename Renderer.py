import pygame as pg
from sys import exit
import numpy as np

# pygame settings
pg.init()
clock = pg.time.Clock()

WIDTH, HEIGHT = 1024, 720
screen = pg.display.set_mode((WIDTH, HEIGHT))


# camera settings
cam_pos = (512, 500)
cam_dir = (0, -1)
cam_fov = 80    # horizontal field-of-view angle in degrees
viewplain_dis = 50

speed = 5
rot_speed = .1

p1 = (512, 300)
p2 = (400, 310)


def move_cam(pos, dir):     # camera controller to move the camera around with the keyboard
    velocity = 0
    rotation = 0

    key_list = pg.key.get_pressed()
    if key_list[pg.K_w]:
        velocity = speed
    elif key_list[pg.K_s]:
        velocity = -speed
    if key_list[pg.K_a]:
        rotation = -rot_speed
    elif key_list[pg.K_d]:
        rotation = rot_speed

    cam_dir_new = rot_vec(dir, rotation)
    cam_pos_new = va(pos, sm(velocity, dir))
    return cam_pos_new, cam_dir_new


def draw_cam():     # displays the camera and its FOV legs to show its direction
    drawpoint(cam_pos, "Yellow", 7)

    fov_leg1_vec = rot_vec(cam_dir, np.deg2rad(cam_fov/2))
    fov_leg1_end = va(cam_pos, sm(2000, fov_leg1_vec))
    drawline(cam_pos, fov_leg1_end)

    fov_leg2_vec = rot_vec(cam_dir, -np.deg2rad(cam_fov / 2))
    fov_leg2_end = va(cam_pos, sm(2000, fov_leg2_vec))
    drawline(cam_pos, fov_leg2_end)


def project_to_screen(point):   # returns the coordinates of the point after being projected to the viewplain
    cam_space_point = va(point, cam_pos, -1)
    point_angle = np.arccos(np.dot(cam_space_point, cam_dir) / (magn(cam_space_point)))

    # checks if the point would be visable and ignores it if not
    if abs(point_angle) < np.deg2rad(cam_fov/2):
        if magn(cam_space_point) >= viewplain_dis:
            stretch_factor = viewplain_dis / (np.dot(cam_space_point, cam_dir))
            scaled_point = va(cam_pos, sm(stretch_factor, cam_space_point))
            return scaled_point


def va(vector1, vector2, sign=1):   # vector-addition
    summed_vector = [vector1[i] + sign*vector2[i] for i in range(len(vector1))]
    return summed_vector


def sm(scalar, vector):     # scalar-multiplication of a vector
    scaled_vector = [scalar * element for element in vector]
    return scaled_vector


def magn(vector):   # get the magnitude of a vector
    magnitude = (np.sum([element**2 for element in vector])) ** 0.5
    return magnitude


def rot_vec(vector, angle):     # rotate a vector, angle in radians
    rot_mat = [[np.cos(angle), -np.sin(angle)],
               [np.sin(angle), np.cos(angle)]]
    new_vector = np.matmul(rot_mat, vector)
    return new_vector


def drawline(start, end, color="White", width=3):
    pg.draw.line(screen, color, start, end, width)


def drawpoint(position, color="White", size=5):
    if position:
        pg.draw.circle(screen, color, position, size)
    else:
        pass


while True:     # main loop in which everything happens
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
    screen.fill("Black")

    cam_pos, cam_dir = move_cam(cam_pos, cam_dir)

    drawpoint(p1)
    drawpoint(project_to_screen(p1))

    drawpoint(p2, "Blue")
    drawpoint(project_to_screen(p2), "Blue")
    draw_cam()

    pg.display.update()
    clock.tick(60)
