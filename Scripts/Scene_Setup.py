import os
from Utils import *
from Camera import Camera
from Models import Model

# Camera Setup----------------------------------------------------------------------------------------------------------
cam = Camera([0, 0, 0])
light_source_dir = norm((0, 200, -500))
environment_light_percent = 0.3  # amount of illumination in spots without direct lighting (value between 0 and 1)
# ----------------------------------------------------------------------------------------------------------------------


# Objects Setup--------------------------------------------------------------------------------------------------------
models = []
plane = convert_obj_file("../Models/VideoShip.obj")
triangle = convert_obj_file("../Models/Triangle.obj")
utah_teapot = convert_obj_file("../Models/Utah Teapot.obj")
mountains = convert_obj_file("../Models/mountains.obj")

# models.append(Model((0, -300, 1000), plane[0], plane[1], (255, 0, 0), 40, np.pi, (0, 1, 0)))
# models.append(Model((0, -250, 1100), plane[0], plane[1], (255, 255, 255), 60))
# models.append(Model((120, -350, 950), plane[0], plane[1], (0, 255, 255), 10))
# models.append(Model((0, 0, 200), plane[0], plane[1], (0, 0, 255), 10))
# models.append(Model((-300, 100, 400), plane[0], plane[1], (0, 255, 0), 90))

models.append(Model((0, 0, 500), triangle[0], triangle[1], scale=1, rot_angle=0))
# models.append(Model((20, 0, 500), triangle[0], triangle[1], color=(255, 100, 0), scale=1))

# models.append(Model((0, -300, 1000), utah_teapot[0], utah_teapot[1], scale=100))
# models.append(Model((0, -5000, 7000), mountains[0], mountains[1], scale=100))
# ----------------------------------------------------------------------------------------------------------------------


# Rasterizer Settings---------------------------------------------------------------------------------------------------
fill_triangles = True
skybox = pg.image.load("../Skyboxes/3x3_raster_image_flipped_upside_down1.jpg")
# ----------------------------------------------------------------------------------------------------------------------


# Raytracer Settings----------------------------------------------------------------------------------------------------
res = (160, 90)  # hor and ver resolution (only whole numbered fractions of window dimensions)
rays = []
# ----------------------------------------------------------------------------------------------------------------------


# PyGame Setup----------------------------------------------------------------------------------------------------------
dims = (1600, 900)
window_pos = ((1920 - dims[0]) / 2, (1080 - dims[1]) / 2)
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % window_pos
window_center = va(window_pos, sm(0.5, dims))  # center of the window in screen coordinates
mouse_pos = [0, 0]
get_mouse_movement()

pg.init()
screen = pg.display.set_mode(dims)
pg.mouse.set_visible(False)

show_fps = True
# ----------------------------------------------------------------------------------------------------------------------
