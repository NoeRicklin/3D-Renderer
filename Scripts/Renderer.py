from Scene_Setup import *
from Rasterizer import rasterizer
from Raytracer import raytracer

while True:  # main loop in which everything happens
    event_checks()
    print_fps()

    get_mouse_movement()
    cam.move_cam()

    rasterizer()

    pg.display.update()
