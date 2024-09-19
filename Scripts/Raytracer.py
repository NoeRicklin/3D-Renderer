from Scene_Setup import *

# screen = {(x, y): (0, 0, 0) for x in range(dims[0]) for y in range(dims[1])}
image = [(50, 90, 210) for x in range(dims[0]) for y in range(dims[1])]
image = pixels = np.array(image, dtype=np.uint8).reshape((dims[0], dims[1], 3))
print(image)

pixel_size_x = int(dims[0] / res[0])
pixel_size_y = int(dims[1] / res[1])
rays = {(x, y): (pixel_size_x * x, pixel_size_y * y) for x in range(res[0]) for y in range(res[1])}

image = pg.surfarray.make_surface(image)
screen.blit(image, (0, 0))


def raytracer():
    screen.blit(image, (0, 0))
