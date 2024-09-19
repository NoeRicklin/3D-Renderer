from Utils import *


class Model:
    def __init__(self, center, vertices, triangles, color=(255, 255, 255), scale=1, rot_angle=0, rot_axis=(0, 1, 0)):
        self.center = center
        self.vertices = [sm(scale, vertex) for vertex in vertices]
        self.color = color
        self.triangles = []
        for triangle in triangles:
            self.triangles.append(Triangle(self, triangle, color))

        self.rot_obj(rot_angle, rot_axis)

    def move_obj_to(self, pos):
        self.center = pos

    def translate_obj(self, translation):
        self.center = va(self.center, translation)

    def rot_obj(self, angle, axis=(0, 1, 0)):   # angle in rad
        self.vertices = [rot_vec(vertex, angle, axis) for vertex in self.vertices]
        for triangle in self.triangles:
            triangle.center = rot_vec(triangle.center, angle, axis)
            triangle.normal = rot_vec(triangle.normal, angle, axis)
            triangle.color = triangle.calc_brightness(triangle.max_color)


class Triangle:
    def __init__(self, parent, vertices, color=(255, 255, 255)):
        self.vertices = vertices
        self.parent = parent
        self.center = self.get_center()   # triangle-center relative to parent-center
        self.normal = self.get_normal()
        self.max_color = pg.Color(color)
        self.color = self.calc_brightness(self.max_color)

    def lcl_vert(self, index):
        return self.parent.vertices[self.vertices[index]]

    def get_center(self):
        points_x = [self.lcl_vert(i)[0] for i in range(3)]
        points_y = [self.lcl_vert(i)[1] for i in range(3)]
        points_z = [self.lcl_vert(i)[2] for i in range(3)]

        center_x = (min(points_x) + (max(points_x) - min(points_x)) / 2)
        center_y = (min(points_y) + (max(points_y) - min(points_y)) / 2)
        center_z = (min(points_z) + (max(points_z) - min(points_z)) / 2)
        return center_x, center_y, center_z

    def get_normal(self):  # vertices are assumed to be defined in clockwise-order when looked at from outside
        v1 = va(self.parent.vertices[self.vertices[1]], self.parent.vertices[self.vertices[0]], sign=-1)
        v2 = va(self.parent.vertices[self.vertices[2]], self.parent.vertices[self.vertices[1]], sign=-1)
        normal_vector = norm(np.cross(v1, v2))
        return normal_vector

    def calc_brightness(self, max_col):
        from Scene_Setup import light_source_dir, environment_light_percent
        clamped_dot = max(0, np.dot(self.normal, light_source_dir))
        return pg.Color(sm(environment_light_percent + clamped_dot - environment_light_percent * clamped_dot, max_col))