from Utils import *


class Camera:
    def __init__(self, pos, dims, mouse_control=True):
        self.pos = pos
        self.right = (1, 0, 0)
        self.up = (0, 1, 0)
        self.dir = (0, 0, 1)
        self.fov = 110  # horizontal field-of-view angle in degrees
        self.viewplane_dis = 200  # distance of the viewplane relative to the camera
        self.viewplane_width = 2 * self.viewplane_dis * np.tan(np.deg2rad(self.fov / 2))  # explained in "Notizen"
        self.viewplane_height = self.viewplane_width * (dims[1] / dims[0])
        self.speed = 1000
        self.rot_speed = .008
        self.mouse_control = mouse_control

    def move_cam(self):  # camera controller to move the camera around with the keyboard
        velocity = [0, 0, 0]
        rotation = [0, 0]  # only 2 values because the camera doesn't need to turn around the z axis
        key_list = pg.key.get_pressed()
        # movement forward/backward
        if key_list[pg.K_w]:
            velocity[2] = self.speed
        elif key_list[pg.K_s]:
            velocity[2] = -self.speed
        # movement right/left
        if key_list[pg.K_d]:
            velocity[0] = self.speed
        elif key_list[pg.K_a]:
            velocity[0] = -self.speed
        # movement up/down
        if key_list[pg.K_SPACE]:
            velocity[1] = self.speed
        elif key_list[pg.K_LSHIFT]:
            velocity[1] = -self.speed

        if self.mouse_control:
            delta_mouse_pos = get_mouse_movement()
            rotation = sm(self.rot_speed, delta_mouse_pos)
        else:
            # rotation left/right
            if key_list[pg.K_LEFT]:
                rotation[1] = -self.rot_speed
            elif key_list[pg.K_RIGHT]:
                rotation[1] = self.rot_speed
            # rotation up/downright
            if key_list[pg.K_DOWN]:
                rotation[0] = -self.rot_speed
            elif key_list[pg.K_UP]:
                rotation[0] = self.rot_speed

        from Utils import dtime
        velocity = sm(dtime, velocity)
        self.rot_cam(rotation)
        move_vec = va(sm(velocity[0], self.right), sm(velocity[1], self.up), sm(velocity[2], self.dir))
        self.pos = va(self.pos, move_vec)

    def rot_cam(self, rotation):
        # apply x-axis rotation
        if rot_vec(self.up, rotation[0], self.right)[1] >= 0:  # makes sure the camera doesn't become upside down
            self.up, self.dir = rot_vec(self.up, rotation[0], self.right), rot_vec(self.dir, rotation[0], self.right)
        # apply y-axis rotation (rotation around the global y-axis so that it doesn't rotate around the z-axis
        self.right = rot_vec(self.right, rotation[1], (0, 1, 0))
        self.up = rot_vec(self.up, rotation[1], (0, 1, 0))
        self.dir = rot_vec(self.dir, rotation[1], (0, 1, 0))

    def vp_rect(self, dims):  # vp stands for viewplane
        vp_width = 2 * self.viewplane_dis * np.tan(np.deg2rad(self.fov / 2))
        vp_height = vp_width / dims[0] * dims[1]
        vp_top_left = (self.pos[0] + self.dir[0] * self.viewplane_dis - self.right[0] * vp_width / 2,
                       self.pos[1] + self.dir[1] * self.viewplane_dis + self.up[1] * vp_height / 2,
                       self.pos[2] + self.dir[2] * self.viewplane_dis - self.right[2] * vp_width / 2)

        return vp_top_left, vp_width, vp_height
