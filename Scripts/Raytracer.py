import numpy as np

from Scene_Setup import *

image = np.zeros((dims[0], dims[1], 3), dtype=int)  # image to be drawn on the screen each frame

pixel_dims = int(dims[0] / res[0]), int(dims[1] / res[1])   # dims of the area drawn by a single ray
rays_pos = np.array([(x*pixel_dims[0], y*pixel_dims[1]) for x in range(res[0]) for y in range(res[1])])
rays_color = np.array([pg.Color(int(ray[0]/dims[0]*255), int(ray[1]/dims[1]*255), 0)[:3] for ray in rays_pos])


def draw_rays():
    for ray_index in range(len(rays_pos)):  # slices arrays to draw whole area of one pixel at once
        x_start, x_end = rays_pos[ray_index][0], rays_pos[ray_index][0]+pixel_dims[0]
        y_start, y_end = rays_pos[ray_index][1], rays_pos[ray_index][1]+pixel_dims[1]
        image[x_start:x_end, y_start:y_end] = rays_color[ray_index]

    image_surf = pg.surfarray.make_surface(image)
    screen.blit(image_surf, (0, 0))


def raytracer():
    draw_rays()
