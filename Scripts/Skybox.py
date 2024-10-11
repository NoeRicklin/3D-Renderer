from Scene_Setup import *

# sets up the skybox
skybox = pg.transform.scale_by(skybox, dims[0] / (cam.fov / 360 * skybox.get_width() / 3))
skybox_dims = (skybox.get_width(), skybox.get_height())
skybox_cutout_width = cam.fov / 360 * skybox_dims[0] / 3
skybox_cutout_height = (cam.fov * dims[1] / dims[0]) / (360 * 3) * skybox_dims[1]


def draw_skybox():
    z_angle = np.arccos(np.dot(cam.dir, (0, 0, 1))) / np.pi * np.sign(cam.dir[0])
    skybox_look_center = va((z_angle * skybox_dims[0] / 6, -cam.dir[1] * skybox_dims[1] / 6), sm(0.5, skybox_dims))
    skybox_cutout_rect_start = va(skybox_look_center, sm(0.5, dims), sign=-1)
    screen.blit(skybox, (0, 0), (skybox_cutout_rect_start, dims))
