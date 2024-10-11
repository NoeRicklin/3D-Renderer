from Scene_Setup import *
from Rasterizer import rasterizer
from Raytracer import raytracer

while True:  # main loop in which everything happens
    event_checks()
    print_fps()

    get_mouse_movement()
    cam.move_cam()

    raytracer()

    # models[0].rot_obj(0.1)

    pg.display.update()
