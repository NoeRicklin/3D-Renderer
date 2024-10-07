from Scene_Setup import *
from Ray import Ray

image = np.zeros((dims[0], dims[1], 3), dtype=int)  # image to be drawn on the screen each frame

pixel_dims = int(dims[0] / res[0]), int(dims[1] / res[1])  # dims of the screenarea drawn by a single ray
vp_pxl_dims = cam.vp_rect(dims)[1] / res[0], cam.vp_rect(dims)[2] / res[1]    # dims of the pixelarea on the viewplane


def setup_rays():
    for x in range(res[0]):
        for y in range(res[1]):
            ray_cam_pos = va(cam.vp_rect(dims)[0], va(sm(x * vp_pxl_dims[0], cam.right), sm(-y * vp_pxl_dims[1], cam.up)))
            ray_pos = va(cam.pos, ray_cam_pos)
            ray_direction = norm(va(ray_pos, cam.pos, sign=-1))
            ray_screen_pos = (x * pixel_dims[0], y * pixel_dims[1])
            ray_color = pg.Color(int(x / res[0] * 255), int(y / res[1] * 255), 0)[:3]

            ray = Ray(ray_cam_pos, ray_pos, ray_direction, ray_screen_pos, ray_color)
            rays.append(ray)


def draw_rays():
    for ray in rays:  # slices arrays to draw whole area of one pixel at once
        for obj in models:
            if ray_box_hit(ray, obj):
                ray.color = (255, 0, 0)
        x_start, x_end = ray.screen_pos[0], ray.screen_pos[0] + pixel_dims[0]
        y_start, y_end = ray.screen_pos[1], ray.screen_pos[1] + pixel_dims[1]
        image[x_start:x_end, y_start:y_end] = ray.color

    image_surf = pg.surfarray.make_surface(image)
    screen.blit(image_surf, (0, 0))


def ray_box_hit(ray, obj):
    faces = get_ray_facing_sides(ray, obj)
    for face in faces:
        if ray_rect_hit(ray, face, obj.center):
            return True
    return False


def ray_rect_hit(ray, rect, obj_center):
    # scales ray.dir to land on the plane on which the rectangle lies
    ray_to_obj = va(obj_center, ray.pos, sign=-1)   # relative position of the ray_start compared to the object
    ray_scalar = (ray_to_obj[rect[3]] + rect[rect[3]]) / ray.dir[rect[3]]
    scaled_dir = sm(ray_scalar, ray.dir)
    if magn(scaled_dir) < cam.viewplane_dis:    # clips of objects too close to the camera
        return False
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
    return False


def get_ray_facing_sides(ray, obj):
    faces = []
    if ray.dir[0] > 0:
        x_face = obj.aabb[0][0], obj.aabb[1], obj.aabb[2], 0    # das Schlusselement gibt die Richtung der Seite an
        faces.append(x_face)
    if ray.dir[0] < 0:
        x_face = obj.aabb[0][1], obj.aabb[1], obj.aabb[2], 0    # das Schlusselement gibt die Richtung der Seite an
        faces.append(x_face)
    if ray.dir[1] > 0:
        y_face = obj.aabb[0], obj.aabb[1][0], obj.aabb[2], 1    # das Schlusselement gibt die Richtung der Seite an
        faces.append(y_face)
    if ray.dir[1] < 0:
        y_face = obj.aabb[0], obj.aabb[1][1], obj.aabb[2], 1    # das Schlusselement gibt die Richtung der Seite an
        faces.append(y_face)
    if ray.dir[2] > 0:
        z_face = obj.aabb[0], obj.aabb[1], obj.aabb[2][0], 2    # das Schlusselement gibt die Richtung der Seite an
        faces.append(z_face)
    if ray.dir[2] < 0:
        z_face = obj.aabb[0], obj.aabb[1], obj.aabb[2][1], 2    # das Schlusselement gibt die Richtung der Seite an
        faces.append(z_face)
    return faces


def set_rays():
    for ray in rays:
        ray.pos = va(cam.pos, ray.cam_pos)
        ray.color = (0, 0, 0)


setup_rays()


def raytracer():
    set_rays()
    draw_rays()
