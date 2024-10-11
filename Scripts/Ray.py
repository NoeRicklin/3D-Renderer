from Utils import *


class PxlRay:
    def __init__(self, cam_pos, pos, cam_dir, dir, screen_pos, color):
        self.cam_pos = cam_pos
        self.pos = pos  # world position
        self.cam_dir = cam_dir
        self.dir = dir
        self.color = color
        self.screen_pos = screen_pos


class BounceRay:
    def __init__(self, pos, dir):
        self.pos = pos
        self.dir = dir
