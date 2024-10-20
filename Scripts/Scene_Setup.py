import os
from Utils import *
from Camera import Camera
from Models import Model

# lightsource Setup----------------------------------------------------------------------------------------------------
light_source_dir = norm((0, 300, -500))
environment_light_percent = 0.3  # amount of illumination in spots without direct lighting (value between 0 and 1)
# ---------------------------------------------------------------------------------------------------------------------


# Objects Setup--------------------------------------------------------------------------------------------------------
models = []
plane = convert_obj_file("../Models/VideoShip.obj")
triangle = convert_obj_file("../Models/Triangle.obj")
square = convert_obj_file("../Models/Square.obj")
# utah_teapot = convert_obj_file("../Models/Utah Teapot.obj")
# mountains = convert_obj_file("../Models/mountains.obj")
# sphere = convert_obj_file("../Models/sphere.obj")
# sphere_high_poly = convert_obj_file("../Models/sphere_high_poly.obj")

# models.append(Model(plane, (0, 0, 200), (255, 0, 0), 20, np.pi, (0.2, 1, -0.5)))
# models.append(Model(plane, (0, -250, 1100), (255, 255, 255), 60))
# models.append(Model(plane, (120, -350, 950), (0, 255, 255), 10))
# models.append(Model(plane, (0, 0, 200), (0, 0, 255), 10))
# models.append(Model(plane, (-300, 100, 400), (0, 255, 0), 90))

models.append(Model(triangle, (0, 0, 450), (60, 180, 25), 1.5, 1))
models.append(Model(triangle, (0, -100, 500), (120, 115, 210), 4))

# models.append(Model(square, (-150, 0, 300), (255, 255, 255), 100, 0))
# models.append(Model(square, (150, 0, 300), (255, 255, 255), 100, 1.2, rot_axis=(1, 0, 0)))

# models.append(Model(sphere, (0, 0, 500), (0, 255, 240), 70))
# models.append(Model(sphere_high_poly, (0, 0, 500), (0, 255, 240), 70))

# models.append(Model(utah_teapot, (0, -300, 1000), scale=100))
# ----------------------------------------------------------------------------------------------------------------------


# Rasterizer Settings---------------------------------------------------------------------------------------------------
fill_triangles = True
skybox = pg.image.load("../Skyboxes/3x3_raster_image_flipped_upside_down1.jpg")
# ----------------------------------------------------------------------------------------------------------------------


# Raytracer Settings----------------------------------------------------------------------------------------------------
res = (160, 90)  # hor and ver resolution (only whole numbers)
highlight_strength = 35
scatter_strength = 1
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


# Camera Setup----------------------------------------------------------------------------------------------------------
cam = Camera([0, 0, 0], dims)
# ----------------------------------------------------------------------------------------------------------------------
