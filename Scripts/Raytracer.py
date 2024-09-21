from Scene_Setup import *
from Ray import Ray

image = np.zeros((dims[0], dims[1], 3), dtype=int)  # image to be drawn on the screen each frame

pixel_dims = int(dims[0] / res[0]), int(dims[1] / res[1])  # dims of the screenarea drawn by a single ray
vp_pixel_dims = cam.vp_rect(dims)[1] / res[0], cam.vp_rect(dims)[2] / res[1]    # dims of the pixelarea on the viewplane


def setup_rays():
    for x in range(res[0]):
        for y in range(res[1]):
            ray_pos = va(cam.vp_rect(dims)[0], va(sm(x*vp_pixel_dims[0], cam.right), sm(y*vp_pixel_dims[1], cam.up)))
            ray_direction = norm(va(ray_pos, cam.pos, sign=-1))
            ray_screen_pos = (x * pixel_dims[0], y * pixel_dims[1])
            ray_color = pg.Color(int(x / res[0] * 255), int(y / res[1] * 255), 0)[:3]

            ray = Ray(ray_pos, ray_direction, ray_screen_pos, ray_color)
            rays.append(ray)


def draw_rays():
    for ray in rays:  # slices arrays to draw whole area of one pixel at once
        x_start, x_end = ray.screen_pos[0], ray.screen_pos[0] + pixel_dims[0]
        y_start, y_end = ray.screen_pos[1], ray.screen_pos[1] + pixel_dims[1]
        image[x_start:x_end, y_start:y_end] = ray.color

    image_surf = pg.surfarray.make_surface(image)
    screen.blit(image_surf, (0, 0))


setup_rays()


def raytracer():
    draw_rays()
