from Scene_Setup import *
from Rasterizer import rasterizer
from Raytracer import raytracer
from Skybox import draw_skybox

while True:  # main loop in which everything happens
    event_checks()
    print_time_per_frame()

    cam.move_cam()

    screen.fill("Black")
    draw_skybox()

    rasterizer()

    pg.display.update()
