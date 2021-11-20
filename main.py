import shapefile
import cv2
import numpy as np
from vincenty import vincenty
from rdp import rdp


def find_nearest_coord(coord, points):
    index = 0
    dist = 10e10
    for i in range(len(points)):
        if (vincenty(coord, points[i]) < dist):
            dist = vincenty(coord, points[i])
            index = i
    return index


def set_start_point(coord, points):
    index = find_nearest_coord(coord, points)
    return np.concatenate((points[index:], points[:index]), axis=0)


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
        [np.array([(min_x + xw_step * i, min_y + yh_step * j) for i in range(int(w_average * ppm))]) for j in
         range(int(h_average * ppm))])

    # отрисовываем контур поля (возможно, стоит указывать ширину линии в метрах)
    draw_contour(img, points, min_x, min_y, xw_step, yh_step, width=1)

    # cv2.imshow('a', img)
    # cv2.waitKey()
    return img, p2c


def get_perimeter_path(img, ppm, obstacle_size=5, angle_radius=5, smoothing=1, rdp_epsilon=1, enable_showing=False):
    image = img.copy()

    cv2.floodFill(image, None, (int(image.shape[1] / 2), int(image.shape[0] / 2)), 255)
    show_image('filled', image, enable_showing)

    # уходим подальше от краёв поля
    kernel_size = int(obstacle_size * ppm)
    image = cv2.erode(image, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)), image)
    show_image('eroded', image, enable_showing)

    # обрезаем углы
    kernel_size = int(angle_radius * ppm)
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)),
                             iterations=smoothing)
    show_image('opened', image, enable_showing)

    # строим путь
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    field_edge = np.array(contours).reshape((-1, 2))
    field_edge = rdp(field_edge, epsilon=rdp_epsilon)

    # визуализируем
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


# масштаб (пикселей на метр)
# влияет на точность
ppm = 2

# выгрузка точек из файлов
points, rect = read_points(path="Trimble/Pole", bbox=True)

# создание изображения и таблицы конвертации
image, convertation_table = create_image(points, rect, ppm=ppm)

# параметры для поиска пути объезда по периметру (крутилки)
# все числа float, кроме smoothing
# расстояние между центром робота и границей поля aka радиус сеялки в метрах [0; inf)
obstacle_size = 20.0
# радиус поворота в метрах [0; inf)
angle_radius = 10.0
# степень сглаживания [1; inf)
smoothing = 1
# степень упрощения пути алгоритмом Рамера-Дугласа-Пекера (0; inf)
rdp_epsilon = 3.0

# поиск пути объезда по периметру
path, pixel_coords = get_perimeter_path(image, ppm, obstacle_size, angle_radius, smoothing, rdp_epsilon)

# перевод координат пути в географические
geo_coords = translate_coords(pixel_coords, convertation_table)

# выбор стартовой точки, наиболее близкой к заданной
start = (26.973208407171384, 53.21215603723456)
geo_coords = set_start_point(start, geo_coords)

# вывод координат пути на экран
print(geo_coords)

# вывод границ поля и полученного пути на экран
cv2.imshow('original_field_edge', image)
cv2.imshow('path', path)

cv2.waitKey()
