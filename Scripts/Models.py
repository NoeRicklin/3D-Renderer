from Utils import *


class Model:
    def __init__(self, verts_and_trgs, center, color=(255, 255, 255), scale=1, rot_angle=0, rot_axis=(0, 1, 0)):
        self.center = center
        self.vertices = [sm(scale, vertex) for vertex in verts_and_trgs[0]]
        self.color = color
        self.triangles = [Triangle(self, triangle, color) for triangle in verts_and_trgs[1]]

        self.rot_obj(rot_angle, rot_axis)

    def move_obj_to(self, pos):
        self.center = pos
        for trg in self.triangles:
            trg.verts_gbl = trg.gbl_verts()


    def translate_obj_by(self, translation):
        self.center = va(self.center, translation)
        for trg in self.triangles:
            trg.verts_gbl = trg.gbl_verts()

    def rot_obj(self, angle, axis=(0, 1, 0)):  # angle in rad
        self.vertices = [rot_vec(vertex, angle, axis) for vertex in self.vertices]
        for trg in self.triangles:
            trg.center = rot_vec(trg.center, angle, axis)
            trg.normal = rot_vec(trg.normal, angle, axis)
            trg.color = trg.calc_brightness(trg.max_color)
            trg.verts_gbl = trg.gbl_verts()
        self.aabb = self.boundingbox()

    def boundingbox(self):  # returns the dimensions of the axis aligned bounding box (AABB)
        min_x, max_x, min_y, max_y, min_z, max_z = 999999, -999999, 999999, -999999, 999999, -999999
        for vertex in self.vertices:
            if vertex[0] < min_x: min_x = vertex[0]
            if vertex[0] > max_x: max_x = vertex[0]
            if vertex[1] < min_y: min_y = vertex[1]
            if vertex[1] > max_y: max_y = vertex[1]
            if vertex[2] < min_z: min_z = vertex[2]
            if vertex[2] > max_z: max_z = vertex[2]
        return (min_x, max_x), (min_y, max_y), (min_z, max_z)


class Triangle:
    def __init__(self, parent, vertices, color=(255, 255, 255)):
        self.parent = parent
        self.verts_ind = vertices
        self.verts_gbl = self.gbl_verts()
        self.center = self.get_center()  # triangle-center relative to parent-center
        self.normal = self.get_normal()
        self.max_color = pg.Color(color)
        self.color = self.calc_brightness(self.max_color)

    def lcl_vert(self, index):
        return self.parent.vertices[self.verts_ind[index]]

    def gbl_verts(self):
        return [va(self.parent.center, self.parent.vertices[self.verts_ind[i]]) for i in range(3)]

    def get_center(self):
        points_x = [self.lcl_vert(i)[0] for i in range(3)]
        points_y = [self.lcl_vert(i)[1] for i in range(3)]
        points_z = [self.lcl_vert(i)[2] for i in range(3)]

        center_x = (min(points_x) + (max(points_x) - min(points_x)) / 2)
        center_y = (min(points_y) + (max(points_y) - min(points_y)) / 2)
        center_z = (min(points_z) + (max(points_z) - min(points_z)) / 2)
        return center_x, center_y, center_z

    def get_normal(self):  # vertices are assumed to be defined in clockwise-order when looked at from outside
        v1 = va(self.parent.vertices[self.verts_ind[1]], self.parent.vertices[self.verts_ind[0]], sign=-1)
        v2 = va(self.parent.vertices[self.verts_ind[2]], self.parent.vertices[self.verts_ind[1]], sign=-1)
        normal_vector = norm(np.cross(v1, v2))
        return normal_vector

    def calc_brightness(self, max_col):
        from Scene_Setup import light_source_dir, environment_light_percent
        clamped_dot = max(0, np.dot(self.normal, light_source_dir))
        return pg.Color(sm(environment_light_percent + clamped_dot - environment_light_percent * clamped_dot, max_col))
