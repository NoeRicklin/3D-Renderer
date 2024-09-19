from Rasterizer import rasterizer
from Raytracer import *

while True:  # main loop in which everything happens
    Event_checks()

    get_mouse_movement()
    cam.move_cam()

    raytracer()

    pg.display.update()