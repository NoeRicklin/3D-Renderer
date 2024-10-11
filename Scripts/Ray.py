class PxlRay:
    def __init__(self, cam_pos, pos, cam_dir, direction, screen_pos, color):
        self.cam_pos = cam_pos
        self.pos = pos  # world position
        self.cam_dir = cam_dir
        self.dir = direction
        self.color = color
        self.screen_pos = screen_pos


class BounceRay:
    def __init__(self, pos, direction):
        self.pos = pos
        self.dir = direction
