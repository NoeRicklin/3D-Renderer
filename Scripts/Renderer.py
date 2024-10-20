from Scene_Setup import *
from Rasterizer import rasterizer
from Raytracer import raytracer
from Skybox import draw_skybox

while True:  # main loop in which everything happens
    event_checks()
    print_fps()

    get_mouse_movement()
    cam.move_cam()

    screen.fill("Black")
    draw_skybox()

    raytracer()

    pg.display.update()
