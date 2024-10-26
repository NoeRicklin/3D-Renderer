from Scene_Setup import *

depth_map = [[None for _ in range(dims[1])] for _ in range(dims[0])]
depth_map_active = []
color_map = [[(0, 0, 0) for _ in range(dims[1])] for _ in range(dims[0])]


def display_objects():
    for obj in objects:
        display_triangles(obj)


def display_triangles(obj):
    for trg in obj.triangles:
        cam2trg = va(va(obj.center, trg.center), cam.pos, sign=-1)
        if np.dot(cam2trg, trg.normal) >= 0:  # trg-side visable?
            continue
        vert1 = project2screen(trg.verts_gbl[0])
        vert2 = project2screen(trg.verts_gbl[1])
        vert3 = project2screen(trg.verts_gbl[2])
        if fill_triangles:
            trg_color = sm(trg.brightness, trg.max_color)
            rasterize_triangle(vert1, vert2, vert3, trg_color)
        elif vert1 and vert2 and vert3:
            draw_triangle_mesh(vert1, vert2, vert3, trg.max_color)


def project2screen(point):
    cam2point = va(point, cam.pos, sign=-1)

    # converts the camera direction vectors into an array, so they can be used in the linear-combination algorithm
    cam_vecs = np.array([[cam.right[i], -cam.up[i], cam.dir[i]] for i in range(3)])
    cam_space_point = np.linalg.solve(cam_vecs, cam2point)
    depth = cam_space_point[2]

    stretch_factor = cam.viewplane_dis / depth
    if not (0 < stretch_factor <= 1):   # checks if point is visable
        return

    cam_space_proj_point = sm(stretch_factor, cam_space_point)[:2]

    viewplane_proj_point = sm(dims[0] / cam.viewplane_width, cam_space_proj_point)
    viewplane_proj_point = va(viewplane_proj_point, sm(.5, dims))  # centers points on screen
    viewplane_proj_point = [round(viewplane_proj_point[0]), round(viewplane_proj_point[1])]

    if 0 <= viewplane_proj_point[0] <= dims[0] and 0 <= viewplane_proj_point[1] <= dims[1]:
        return viewplane_proj_point + [depth]


def rasterize_triangle(p1, p2, p3, color):
    if not (p1 and p2 and p3) or p1[0] == p2[0] == p3[0]:
        return
    edge_points = calc_linepoints(p2, p1) + calc_linepoints(p3, p1) + calc_linepoints(p3, p2)
    edge_points = sorted(edge_points, key=lambda _: _[0])

    trg_length = edge_points[-1][0] - edge_points[0][0] + 1
    edge_point_index = 0
    for column_index in range(trg_length - 1):
        column_x_pos = column_index + edge_points[0][0]
        column_border_points = []
        while (point := edge_points[edge_point_index])[0] == column_x_pos:
            column_border_points.append(point)
            edge_point_index += 1

        column_border_points = sorted(column_border_points, key=lambda _: _[1])
        bottom_pxl = column_border_points[0]
        top_pxl = column_border_points[-1]

        for height in range(bottom_pxl[1], top_pxl[1]):
            pixel_pos = (column_x_pos, height)
            current_depth = bottom_pxl[2] + (top_pxl[2] - bottom_pxl[2]) / (top_pxl[1] - bottom_pxl[1]) * (height - bottom_pxl[1])

            if min_depth := depth_map[pixel_pos[0]][pixel_pos[1]]:
                if current_depth < float(str(min_depth)):  # type conversions to avoid error warning
                    depth_map[pixel_pos[0]][pixel_pos[1]] = current_depth
                    color_map[pixel_pos[0]][pixel_pos[1]] = color[:3]
            else:
                depth_map[pixel_pos[0]][pixel_pos[1]] = current_depth
                color_map[pixel_pos[0]][pixel_pos[1]] = color[:3]
                depth_map_active.append(pixel_pos)


def draw_triangle_mesh(p1, p2, p3, color):
    drawpoint(p1[:2], color)
    drawpoint(p2[:2], color)
    drawpoint(p3[:2], color)
    drawline(p1[:2], p2[:2], color)
    drawline(p1[:2], p3[:2], color)
    drawline(p2[:2], p3[:2], color)


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
    display_objects()
    set_image()
