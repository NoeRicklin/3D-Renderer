from Utils import *


class Ray:
    def __init__(self, pos, dir, screen_pos, color):
        self.pos = pos
        self.dir = dir
        self.color = color
        self.screen_pos = screen_pos

