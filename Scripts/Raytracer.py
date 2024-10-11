from Scene_Setup import *
from Ray import *

image = np.zeros((dims[0], dims[1], 3), dtype=int)  # image to be drawn on the screen each frame

pixel_dims = int(dims[0] / res[0]), int(dims[1] / res[1])  # dims of the screenarea drawn by a single ray
vp_pxl_dims = cam.vp_rect(dims)[1] / res[0], cam.vp_rect(dims)[2] / res[1]    # dims of the pixelarea on the viewplane


def setup_rays():
    for x in range(res[0]):
        for y in range(res[1]):
            ray_cam_xy = va(sm(x * vp_pxl_dims[0], cam.right), sm(-y * vp_pxl_dims[1], cam.up))
            ray_cam_pos = va(cam.vp_rect(dims)[0], ray_cam_xy)
            ray_pos = va(cam.pos, ray_cam_pos)
            ray_cam_dir = norm(va(ray_pos, cam.pos, sign=-1))
            ray_dir = ray_cam_dir
            ray_screen_pos = (x * pixel_dims[0], y * pixel_dims[1])
            ray_color = pg.Color(int(x / res[0] * 255), int(y / res[1] * 255), 0)[:3]

            ray = PxlRay(ray_cam_pos, ray_pos, ray_cam_dir, ray_dir, ray_screen_pos, ray_color)
            rays.append(ray)
    # x, y = 82, 47
    # ray_cam_xy = va(sm(x * vp_pxl_dims[0], cam.right), sm(-y * vp_pxl_dims[1], cam.up))
    # ray_cam_pos = va(cam.vp_rect(dims)[0], ray_cam_xy)
    # ray_pos = va(cam.pos, ray_cam_pos)
    # ray_cam_dir = norm(va(ray_pos, cam.pos, sign=-1))
    # ray_dir = ray_cam_dir
    # ray_screen_pos = (x * pixel_dims[0], y * pixel_dims[1])
    # ray_color = pg.Color(int(x / res[0] * 255), int(y / res[1] * 255), 0)[:3]
    #
    # ray = PxlRay(ray_cam_pos, ray_pos, ray_cam_dir, ray_dir, ray_screen_pos, ray_color)
    # rays.append(ray)


def draw_rays():
    for ray in rays:
        set_ray_color(ray)

        x_start, x_end = ray.screen_pos[0], ray.screen_pos[0] + pixel_dims[0]
        y_start, y_end = ray.screen_pos[1], ray.screen_pos[1] + pixel_dims[1]
        image[x_start:x_end, y_start:y_end] = ray.color

    image_surf = pg.surfarray.make_surface(image)
    screen.blit(image_surf, (0, 0))


def set_ray_color(ray):
    # if ray.screen_pos == (82*pixel_dims[0], 47*pixel_dims[1]):
    #     ray.color = (255, 0, 0)
    #     return
    hit_point, hit_norm, trg_color = find_ray_collision(ray)
    if not hit_point:
        if (look_sun := dot(ray.dir, light_source_dir)) > 0.999:
            ray.color = sm(look_sun**1000, (255, 255, 140))
        return
    brightness = calc_brightness(ray, hit_point, hit_norm)
    ray.color = sm(brightness, trg_color)


def find_ray_collision(ray):
    nearest_hitpoint = None
    nearest_hit_norm = None
    nearest_hit_trg_color = None
    for obj in models:
        if not ray_box_hit(ray, obj):  # checks if the ray hits the bounding box of the object
            continue
        hit_point, hit_norm, hit_color = ray_obj_hit(ray, obj)  # calculates the point where the ray hits the object
        if not hit_point:
            continue
        if nearest_hitpoint and nearest_hitpoint[1] <= hit_point[1]:
            continue
        nearest_hitpoint = hit_point
        nearest_hit_norm = hit_norm
        nearest_hit_trg_color = hit_color
    return nearest_hitpoint, nearest_hit_norm, nearest_hit_trg_color


def ray_box_hit(ray, obj):
    faces = get_ray_facing_sides(ray, obj)
    for face in faces:
        if ray_rect_hit(ray, face, obj.center):
            return True
    if check_point_in_aabb(ray.pos, obj.center, obj.aabb):
        return True


def get_ray_facing_sides(ray, obj):
    faces = []
    aabb = obj.aabb
    if ray.dir[0] > 0:
        x_face = aabb[0][0], aabb[1], aabb[2], 0    # das Schlusselement gibt die Richtung der Seite an
        faces.append(x_face)
    if ray.dir[0] < 0:
        x_face = aabb[0][1], aabb[1], aabb[2], 0    # das Schlusselement gibt die Richtung der Seite an
        faces.append(x_face)
    if ray.dir[1] > 0:
        y_face = aabb[0], aabb[1][0], aabb[2], 1    # das Schlusselement gibt die Richtung der Seite an
        faces.append(y_face)
    if ray.dir[1] < 0:
        y_face = aabb[0], aabb[1][1], aabb[2], 1    # das Schlusselement gibt die Richtung der Seite an
        faces.append(y_face)
    if ray.dir[2] > 0:
        z_face = aabb[0], aabb[1], aabb[2][0], 2    # das Schlusselement gibt die Richtung der Seite an
        faces.append(z_face)
    if ray.dir[2] < 0:
        z_face = aabb[0], aabb[1], aabb[2][1], 2    # das Schlusselement gibt die Richtung der Seite an
        faces.append(z_face)
    return faces


def ray_rect_hit(ray, rect, obj_center):
    # scales ray.dir to land on the plane on which the rectangle lies
    ray_to_obj = va(obj_center, ray.pos, sign=-1)   # relative position of the ray_start compared to the object
    ray_scalar = (ray_to_obj[rect[3]] + rect[rect[3]]) / ray.dir[rect[3]]
    if ray_scalar < 0:    # clips of objects too close to the camera
        return False
    scaled_dir = sm(ray_scalar, ray.dir)
    scaled_dir_to_obj = va(scaled_dir, ray_to_obj, sign=-1)

    # checks if the ray landed inside the rectangle
    if rect[3] == 0:
        if (rect[1][0] <= scaled_dir_to_obj[1] <= rect[1][1]) and (rect[2][0] <= scaled_dir_to_obj[2] <= rect[2][1]):
            return True
    elif rect[3] == 1:
        if (rect[0][0] <= scaled_dir_to_obj[0] <= rect[0][1]) and (rect[2][0] <= scaled_dir_to_obj[2] <= rect[2][1]):
            return True
    elif rect[3] == 2:
        if (rect[0][0] <= scaled_dir_to_obj[0] <= rect[0][1]) and (rect[1][0] <= scaled_dir_to_obj[1] <= rect[1][1]):
            return True


def ray_obj_hit(ray, obj):
    nearest_hit_point = None
    hit_surf_normal = None
    color = None

    for trg in obj.triangles:
        if dot(ray.dir, trg.normal) > 0 - 0.00001:   # checks if the triangle is facing the camera
            continue
        if trg_hit := ray_trg_hit(ray, obj, trg):
            if not nearest_hit_point or nearest_hit_point[1] > trg_hit[1]:
                nearest_hit_point = trg_hit
                hit_surf_normal = trg.normal
                color = trg.max_color[:3]
    return nearest_hit_point, hit_surf_normal, color


def ray_trg_hit(ray, obj, trg):
    trg_v0 = obj.vertices[trg.vertices[0]]
    trg_v1 = obj.vertices[trg.vertices[1]]
    trg_v2 = obj.vertices[trg.vertices[2]]

    # scales ray.dir to land on the plane on which the triangle lies and checks if the ray landed inside the triangle
    trg_vec1 = va(trg_v1, trg_v0, sign=-1)
    trg_vec2 = va(trg_v2, trg_v0, sign=-1)

    lin_alg_coefficients = np.array([[ray.dir[i], -trg_vec1[i], -trg_vec2[i]] for i in range(3)])
    lin_alg_sums = np.array(va(va(obj.center, trg_v0), ray.pos, sign=-1))

    # checks if the scaled ray.dir landed in the triangle and if so returns its position
    ray_dir_scalar, trg_vec1_scalar, trg_vec2_scalar = np.linalg.solve(lin_alg_coefficients, lin_alg_sums)
    if ray_dir_scalar <= 0 + 0.00001:
        return
    if trg_vec1_scalar >= 0 and trg_vec2_scalar >= 0 and trg_vec1_scalar + trg_vec2_scalar <= 1:
        hit_point = va(obj.center, trg_v0, va(sm(trg_vec1_scalar, trg_vec1), sm(trg_vec2_scalar, trg_vec2)))
        hit_dis = magn(va(hit_point, ray.pos, sign=-1))
        return hit_point, hit_dis


def calc_brightness(ray, hit_point, surf_norm):
    if not dot(surf_norm, light_source_dir) > 0 - 0.00001:
        return environment_light_percent
    if not check_open_light(hit_point[0]):
        return environment_light_percent
    directly_lit_amount = calc_directly_lit_prob(ray, surf_norm)
    lit_amount = clamp(directly_lit_amount + environment_light_percent, [0, 1])
    return lit_amount


def check_open_light(hit_point):
    ray_to_light = BounceRay(hit_point, light_source_dir)
    return not find_ray_collision(ray_to_light)[0]


def calc_directly_lit_prob(ray, surf_norm):
    reflected_ray_dir = refl_ray(ray, surf_norm)
    reflect_to_light_prob = dot(reflected_ray_dir, light_source_dir) ** highlight_strength
    scatter_amount = dot(surf_norm, light_source_dir) ** (1/scatter_strength)
    lit_prob = (reflect_to_light_prob + scatter_amount) / 2
    return lit_prob


def refl_ray(ray, surf_norm):
    n = surf_norm
    r = ray.dir

    r_reflected = va(sm(2, va(r, sm(dot(r, n), n), sign=-1)), r, sign=-1)
    return r_reflected


def check_point_in_aabb(point, obj_center, aabb):
    check_axis = [obj_center[i] + aabb[i][0] <= point[i] <= obj_center[i] + aabb[i][1] for i in range(3)]
    if check_axis[0] and check_axis[1] and check_axis[2]:
        return True


def draw_aabb():
    from Rasterizer import project_to_screen
    for obj in models:
        obj_verts = []
        for vert_ind in range(8):
            vert_ind_bin = np.binary_repr(vert_ind, 3)
            vertex = [obj.aabb[i][int(vert_ind_bin[i])] for i in range(3)]
            obj_verts.append(vertex)
        obj_screen_verts = []
        for vert in obj_verts:
            try:
                screen_vert = project_to_screen(va(obj.center, vert))[:2]
            except TypeError:
                screen_vert = (0, 0)
            obj_screen_verts.append(screen_vert)
        for vert_ind in range(64):
            vert_ind_oct = np.base_repr(vert_ind, 8, 2)
            drawline(obj_screen_verts[int(vert_ind_oct[-2])], obj_screen_verts[int(vert_ind_oct[-1])])


def set_rays():     # prepares the rays for the new frame
    for ray in rays:
        ray.pos = va(cam.pos, ray.cam_pos)
        ray.dir = va(sm(ray.cam_dir[0], cam.right), sm(ray.cam_dir[1], cam.up), sm(ray.cam_dir[2], cam.dir))
        ray.color = (0, 0, 0)


setup_rays()


def raytracer():
    set_rays()
    draw_rays()
    # draw_aabb()
