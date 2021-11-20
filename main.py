import shapefile
import cv2
import numpy as np
from vincenty import vincenty
from rdp import rdp


def show_image(name, image, enable_showing):
    if (enable_showing):
        cv2.imshow(name, image)


def read_points(path="Trimble/Pole", bbox=False):
    sf = shapefile.Reader(path)
    s = sf.shape(0)
    points = s.points
    rect = sf.bbox
    if (bbox):
        return points, rect
    else:
        return points


def draw_contour(img, points, min_x, min_y, xw_step, yh_step, width=1):
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        x1 = int(round((p1[0] - min_x) / xw_step))
        y1 = int(round((p1[1] - min_y) / yh_step))
        x2 = int(round((p2[0] - min_x) / xw_step))
        y2 = int(round((p2[1] - min_y) / yh_step))
        cv2.line(img, (x1, y1), (x2, y2), 255, width)


def create_image(points, rect, ppm=1):
    borders = 2 * 10e-6
    min_x, max_x = rect[0], rect[2]
    min_y, max_y = rect[1], rect[3]
    min_x -= borders
    min_y -= borders
    max_x += borders
    max_y += borders
    h1 = vincenty((min_x, min_y), (min_x, max_y))
    h2 = vincenty((max_x, min_y), (max_x, max_y))
    w1 = vincenty((min_x, min_y), (max_x, min_y))
    w2 = vincenty((min_x, max_y), (max_x, max_y))

    # метры в высоту и в ширину
    h_average = int((h1 + h2) * 1000 / 2)
    w_average = int((w1 + w2) * 1000 / 2)

    # константные шаги (перевод координат в пиксели)
    xw_step = (max_x - min_x) / (w_average * ppm)
    yh_step = (max_y - min_y) / (h_average * ppm)

    # создание картинки
    size = (int(h_average * ppm + 1), int(w_average * ppm + 1))
    img = np.zeros(size, np.uint8)

    # таблица совместимости пиксель-координата
    p2c = np.array(
        [np.array([(min_x + xw_step * i, min_y + yh_step * j) for i in range(w_average * ppm)]) for j in
         range(h_average * ppm)])

    # отрисовываем контур поля (возможно, стоит указывать ширину линии в метрах)
    draw_contour(img, points, min_x, min_y, xw_step, yh_step, width=1)

    # cv2.imshow('a', img)
    # cv2.waitKey()
    return img, p2c


def get_perimeter_path(img, ppm, rdp_epsilon=1, obstacle_size=5, enable_showing=False):
    image = img.copy()

    cv2.floodFill(image, None, (int(image.shape[1] / 2), int(image.shape[0] / 2)), 255)
    show_image('filled', image, enable_showing)

    kernel_size = obstacle_size * ppm
    cv2.erode(image, np.ones((kernel_size, kernel_size), np.uint8), image)
    show_image('eroded', image, enable_showing)

    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    field_edge = np.array(contours).reshape((-1, 2))
    field_edge = rdp(field_edge, epsilon=rdp_epsilon)

    path = np.zeros(image.shape, np.uint8)
    for i in range(len(field_edge) - 1):
        p1 = field_edge[i]
        p2 = field_edge[i + 1]
        cv2.line(path, p1, p2, 255, 1)
    show_image('path', path, enable_showing)

    return path, field_edge


def translate_coords(pixel_coords, convertation_table):
    geo_coords = []
    for point in pixel_coords:
        geo_coords.append(np.array(convertation_table[point[1]][point[0]]))
    return np.array(geo_coords)


# крутилки
ppm = 2

points, rect = read_points(bbox=True)
image, convertation_table = create_image(points, rect, ppm=ppm)

path, pixel_coords = get_perimeter_path(image, ppm, obstacle_size=30, rdp_epsilon=5)

geo_coords = translate_coords(pixel_coords, convertation_table)
print(geo_coords)

cv2.imshow('original_field_edge', image)
cv2.imshow('path', path)

cv2.waitKey()
