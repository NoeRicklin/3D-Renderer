from Scene_Setup import *

depth_map = [[None for _ in range(dims[1])] for _ in range(dims[0])]
color_map = [[(0, 0, 0) for _ in range(dims[1])] for _ in range(dims[0])]


def display_models(objs):
    objs.sort(key=lambda instance: magn(va(instance.center, cam.pos, sign=-1)), reverse=True)
    for obj in objs:
        display_triangles(obj)
    for pixel in depth_map_active:
        screen.set_at(pixel, color_map[pixel[0]][pixel[1]])
        depth_map[pixel[0]][pixel[1]] = None
        color_map[pixel[0]][pixel[1]] = (0, 0, 0)


def display_triangles(obj):
    for triangle in obj.triangles:
        if np.dot(va(va(obj.center, triangle.center), cam.pos, sign=-1),
                  triangle.normal) < 0:  # trg facing cam?
            vert1 = project_to_screen(va(obj.center, obj.vertices[triangle.vertices[0]]))
            vert2 = project_to_screen(va(obj.center, obj.vertices[triangle.vertices[1]]))
            vert3 = project_to_screen(va(obj.center, obj.vertices[triangle.vertices[2]]))
            if fill_triangles:
                drawtriangle(vert1, vert2, vert3, triangle.color)
            else:
                if vert1 and vert2 and vert3:
                    drawpoint(vert1[:2], triangle.max_color)
                    drawpoint(vert2[:2], triangle.max_color)
                    drawpoint(vert3[:2], triangle.max_color)
                    drawline(vert1[:2], vert2[:2], triangle.max_color, width=3)
                    drawline(vert1[:2], vert3[:2], triangle.max_color, width=3)
                    drawline(vert2[:2], vert3[:2], triangle.max_color, width=3)


def project_to_screen(point):
    # converts the cameravectors into a list so that they can be used in the linear-combination algorhythm
    cam_vecs = np.array([[cam.right[i], cam.up[i], cam.dir[i]] for i in range(3)])
    cam_space_point = np.linalg.solve(cam_vecs, va(point, cam.pos, sign=-1))

    cam_dir_and_point_dot = np.dot(cam_space_point, (0, 0, 1))
    # cam_dir_and_point_angle = np.arccos(cam_dir_and_point_dot/(magn(cam_space_point)))

    if cam_dir_and_point_dot > 0:  # checks if the point is visable
        depth = cam_space_point[2]

        stretch_factor = cam.viewplane_dis / cam_dir_and_point_dot
        cam_space_proj_point = sm(stretch_factor, cam_space_point)
        cam_space_proj_point = cam_space_proj_point[:2]  # reduces point to 2D

        viewplane_width = 2 * cam.viewplane_dis * np.tan(
            np.deg2rad(cam.fov / 2))  # Formula explained in "Notizen"
        viewplane_height = viewplane_width * (dims[1] / dims[0])

        cam_space_proj_point = (dims[0] * (cam_space_proj_point[0] / viewplane_width),
                                dims[1] * (cam_space_proj_point[1] / viewplane_height))

        cam_space_proj_point = (cam_space_proj_point[0], -cam_space_proj_point[1])  # flips image (pygame-BS)
        cam_space_proj_point = va(sm(1, cam_space_proj_point), sm(.5, dims))  # centers points on screen
        cam_space_proj_point = [round(cam_space_proj_point[0]), round(cam_space_proj_point[1])]
        if 0 <= cam_space_proj_point[0] <= dims[0] and 0 <= cam_space_proj_point[1] <= dims[1]:
            return cam_space_proj_point + [depth]


def drawtriangle(p1, p2, p3, color):
    if p1 and p2 and p3:
        if p1[0] == p2[0] == p3[0]:
            return
        line_points = sorted(calc_line_points(p2, p1) + calc_line_points(p3, p1) + calc_line_points(p3, p2),
                             key=lambda x: x[0])
        trg_length = line_points[-1][0] - line_points[0][0] + 1
        last_row_point_index = 0

        for row_index in range(trg_length - 1):
            row_edge_points = []
            while (point := line_points[last_row_point_index])[0] == row_index + line_points[0][0]:
                row_edge_points.append(point)
                last_row_point_index += 1
            row_edge_points = sorted(row_edge_points, key=lambda x: x[1])
            row_height_range = row_edge_points[0][1], row_edge_points[-1][1]
            for height in range(row_height_range[0], row_height_range[1]):
                pixel_pos = (row_index + line_points[0][0], height)
                current_depth = (row_edge_points[0][2] + (row_edge_points[-1][2] - row_edge_points[0][2]) /
                                 (row_edge_points[-1][1] - row_edge_points[0][1]) * (
                                         height - row_edge_points[0][1]))

                if depth_map[pixel_pos[0]][pixel_pos[1]]:
                    if current_depth < depth_map[pixel_pos[0]][pixel_pos[1]]:
                        depth_map[pixel_pos[0]][pixel_pos[1]] = current_depth
                        color_map[pixel_pos[0]][pixel_pos[1]] = color[:3]
                else:
                    depth_map[pixel_pos[0]][pixel_pos[1]] = current_depth
                    color_map[pixel_pos[0]][pixel_pos[1]] = color[:3]
                    depth_map_active.append(pixel_pos)


def calc_line_points(start, end):
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


skybox = pg.image.load("../Skyboxes/3x3_raster_image_flipped_upside_down1.jpg")
skybox = pg.transform.scale_by(skybox, dims[0] / (cam.fov / 360 * skybox.get_width() / 3))
skybox_dims = (skybox.get_width(), skybox.get_height())
skybox_cutout_width = cam.fov / 360 * skybox_dims[0] / 3
skybox_cutout_height = (cam.fov * dims[1] / dims[0]) / (360 * 3) * skybox_dims[1]


def draw_skybox():
    z_angle = np.arccos(np.dot(cam.dir, (0, 0, 1))) / np.pi * np.sign(cam.dir[0])
    skybox_look_center = va((z_angle * skybox_dims[0] / 6, -cam.dir[1] * skybox_dims[1] / 6), sm(0.5, skybox_dims))
    skybox_cutout_rect_start = va(skybox_look_center, sm(0.5, dims), sign=-1)
    screen.blit(skybox, (0, 0), (skybox_cutout_rect_start, dims))


while True:  # main loop in which everything happens
    running_checks()

    get_mouse_movement()
    cam.move_cam()

    draw_skybox()
    depth_map_active = []
    display_models(models)

    pg.display.update()
    calc_fps(False)
