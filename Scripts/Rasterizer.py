from Scene_Setup import *
from Skybox import draw_skybox

depth_map = [[None for _ in range(dims[1])] for _ in range(dims[0])]
depth_map_active = []
color_map = [[(0, 0, 0) for _ in range(dims[1])] for _ in range(dims[0])]


def display_models():
    for obj in models:
        display_triangles(obj)


def display_triangles(obj):
    for trg in obj.triangles:
        if np.dot(va(va(obj.center, trg.center), cam.pos, sign=-1), trg.normal) >= 0:  # trg facing cam?
            continue
        vert1 = project_to_screen(va(obj.center, obj.vertices[trg.vertices[0]]))
        vert2 = project_to_screen(va(obj.center, obj.vertices[trg.vertices[1]]))
        vert3 = project_to_screen(va(obj.center, obj.vertices[trg.vertices[2]]))
        if fill_triangles:
            rasterize_triangle(vert1, vert2, vert3, trg.color)
            continue
        if vert1 and vert2 and vert3:
            drawpoint(vert1[:2], trg.max_color)
            drawpoint(vert2[:2], trg.max_color)
            drawpoint(vert3[:2], trg.max_color)
            drawline(vert1[:2], vert2[:2], trg.max_color)
            drawline(vert1[:2], vert3[:2], trg.max_color)
            drawline(vert2[:2], vert3[:2], trg.max_color)


def project_to_screen(point):
    # converts the cameravectors into a list so that they can be used in the linear-combination algorhythm
    cam_vecs = np.array([[cam.right[i], cam.up[i], cam.dir[i]] for i in range(3)])
    cam_space_point = np.linalg.solve(cam_vecs, va(point, cam.pos, sign=-1))

    cam_dir_and_point_dot = np.dot(cam_space_point, (0, 0, 1))

    if cam_dir_and_point_dot > 0:  # checks if the point is visable
        depth = cam_space_point[2]

        stretch_factor = cam.viewplane_dis / cam_dir_and_point_dot
        cam_space_proj_point = sm(stretch_factor, cam_space_point)
        cam_space_proj_point = cam_space_proj_point[:2]  # reduces point to 2D

        viewplane_width = 2 * cam.viewplane_dis * np.tan(
            np.deg2rad(cam.fov / 2))  # Formula explained in "Notizen"
        viewplane_height = viewplane_width * (dims[1] / dims[0])

        cam_space_proj_point = (dims[0] * (cam_space_proj_point[0] / viewplane_width),
                                -dims[1] * (cam_space_proj_point[1] / viewplane_height))

        cam_space_proj_point = va(sm(1, cam_space_proj_point), sm(.5, dims))  # centers points on screen
        cam_space_proj_point = [round(cam_space_proj_point[0]), round(cam_space_proj_point[1])]
        if 0 <= cam_space_proj_point[0] <= dims[0] and 0 <= cam_space_proj_point[1] <= dims[1]:
            return cam_space_proj_point + [depth]


def rasterize_triangle(p1, p2, p3, color):
    if not (p1 and p2 and p3) or p1[0] == p2[0] == p3[0]:
        return
    line_points = calc_linepoints(p2, p1) + calc_linepoints(p3, p1) + calc_linepoints(p3, p2)
    line_points = sorted(line_points, key=lambda _: _[0])
    trg_length = line_points[-1][0] - line_points[0][0] + 1
    last_column_point_index = 0

    for column_index in range(trg_length - 1):
        column_edge_points = []
        while (point := line_points[last_column_point_index])[0] == column_index + line_points[0][0]:
            column_edge_points.append(point)
            last_column_point_index += 1
        column_edge_points = sorted(column_edge_points, key=lambda _: _[1])
        column_height_range = column_edge_points[0][1], column_edge_points[-1][1]
        for height in range(column_height_range[0], column_height_range[1]):
            pixel_pos = (column_index + line_points[0][0], height)
            a = column_edge_points[0]
            b = column_edge_points[-1]
            current_depth = (a[2] + (b[2] - a[2]) / (b[1] - a[1]) * (height - a[1]))

            if min_depth := depth_map[pixel_pos[0]][pixel_pos[1]]:
                if current_depth < float(str(min_depth)):   # type conversions to avoid error warning
                    depth_map[pixel_pos[0]][pixel_pos[1]] = current_depth
                    color_map[pixel_pos[0]][pixel_pos[1]] = color[:3]
            else:
                depth_map[pixel_pos[0]][pixel_pos[1]] = current_depth
                color_map[pixel_pos[0]][pixel_pos[1]] = color[:3]
                depth_map_active.append(pixel_pos)


def calc_linepoints(start, end):
    line_points = []
    if start[0] == end[0]:
        start, end = sorted([start, end], key=lambda x: x[1])
        line_points = [(start[0], height, start[2]) for height in range(start[1], end[1])]
        return line_points

    start, end = sorted([start, end], key=lambda x: x[0])
    if abs(end[0] - start[0]) >= abs(end[1] - start[1]):  # if slope <= 1
        slope = (end[1] - start[1]) / (end[0] - start[0])
        for pixel_index in range(end[0] - start[0] + 1):
            pixel_height = round(slope * pixel_index)

            pixel_depth = start[2] + ((end[2] - start[2]) / (end[0] - start[0])) * pixel_index
            pixel_pos = [start[0] + pixel_index, start[1] + pixel_height]
            line_points.append(pixel_pos + [pixel_depth])
    else:  # if slope > 1
        start, end = sorted([start, end], key=lambda x: x[1])
        slope = (start[0] - end[0]) / (end[1] - start[1])
        for pixel_index in range(end[1] - start[1] + 1):
            pixel_height = round(slope * pixel_index)

            pixel_depth = start[2] + ((end[2] - start[2]) / (end[1] - start[1])) * pixel_index
            pixel_pos = [start[0] - pixel_height, start[1] + pixel_index]
            line_points.append(pixel_pos + [pixel_depth])
    return line_points


def set_image():
    global depth_map_active
    for pixel in depth_map_active:
        screen.set_at(pixel, color_map[pixel[0]][pixel[1]])
        depth_map[pixel[0]][pixel[1]] = None
        color_map[pixel[0]][pixel[1]] = (0, 0, 0)
    depth_map_active = []


def rasterizer():
    draw_skybox()
    display_models()
    set_image()
