from Utils import *
from Camera import Camera
from Objects import Object

# lightsource Setup-----------------------------------------------------------------------------------------------------
light_source_dir = norm((0, 00, -500))     # direction to the lightsource
environment_light_percent = 0.3  # amount of illumination in spots without direct lighting (value between 0 and 1)
reflectivity = 4    # high number means less scattering
# ----------------------------------------------------------------------------------------------------------------------


# Objects Setup---------------------------------------------------------------------------------------------------------
objects = []


# Notation für ein Model:
# <name> = modelfile2object("<Speicherort der Modeldatei>")

# Notation für ein Objekt:
# objects.append(Object(<name>, <Position>, [<Farbe>], [<Grösse>], [<Drehwinkel>], [<Drehachse>]))
#   * Parameter in eckigen Klammern sind optional


plane = modelfile2object("../Models/VideoShip.obj")
triangle = modelfile2object("../Models/Triangle.obj")
square = modelfile2object("../Models/Square.obj")
utah_teapot = modelfile2object("../Models/Utah Teapot.obj")
sphere = modelfile2object("../Models/sphere.obj")
sphere_high_poly = modelfile2object("../Models/sphere_high_poly.obj")

objects.append(Object(plane, (0, 0, 400), (255, 0, 0), 30, np.pi, (0.2, 1, -0.5)))
# objects.append(Object(plane, (-500, 0, 1100), (255, 255, 255), 60, np.pi/2, (1, 1, 0)))
# objects.append(Object(plane, (500, 0, 1100), (255, 255, 255), 60, -np.pi/2, (1, 1, 0)))
# objects.append(Object(plane, (120, -350, 950), (0, 255, 255), 10))
# objects.append(Object(plane, (0, 0, 200), (0, 0, 255), 10))
# objects.append(Object(plane, (0, 100, 400), (0, 255, 0), 90, np.pi, (0.2, 1, -0.5)))

# objects.append(Object(triangle, (0, 0, 450), (60, 180, 25), 1.5, 1))
# objects.append(Object(triangle, (0, -100, 500), (120, 115, 210), 4))

# objects.append(Object(square, (-150, 0, 300), (255, 255, 255), 100, 0))
# objects.append(Object(square, (150, 0, 300), (255, 255, 255), 100, 1.2, rot_axis=(1, 0, 0)))

# objects.append(Object(sphere, (0, 0, 500), (0, 255, 240), 50))
# objects.append(Object(sphere_high_poly, (0, 0, 500), (0, 255, 240), 70))

# objects.append(Object(utah_teapot, (0, -300, 1000), scale=100))
# ----------------------------------------------------------------------------------------------------------------------


# Rasterizer Settings---------------------------------------------------------------------------------------------------
fill_triangles = True   # set to false for quicker rendering
skybox = pg.image.load("../Skyboxes/Skybox simple.jpg")
# ----------------------------------------------------------------------------------------------------------------------


# Raytracer Settings----------------------------------------------------------------------------------------------------
res = (160, 90)  # horizontal and vertical resolution (only whole numbers)
highlight_strength = 30    # large number -> small and intense highlight
# ----------------------------------------------------------------------------------------------------------------------


# PyGame Setup----------------------------------------------------------------------------------------------------------
dims = (1600, 900)  # dimensions of the window
window_pos = ((1920 - dims[0]) / 2, (1080 - dims[1]) / 2)
window_center = sm(0.5, dims)

pg.init()
screen = pg.display.set_mode(dims)
pg.mouse.set_visible(False)

show_time_per_frame = True
# ----------------------------------------------------------------------------------------------------------------------


# Camera Setup----------------------------------------------------------------------------------------------------------
cam = Camera(dims)
# ----------------------------------------------------------------------------------------------------------------------
