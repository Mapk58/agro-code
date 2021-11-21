import shapefile
import cv2
import numpy as np
from vincenty import vincenty
from rdp import rdp
from math import *
from itertools import groupby


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
    return np.concatenate((points[index:], points[:index + 1]), axis=0)


def show_image(name, image, enable_showing):
    if (enable_showing):
        cv2.imshow(name, image)


def read_points(path, bbox=False):
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
    kernel_size = int(obstacle_size * ppm) * 2
    image = cv2.erode(image, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)), image)
    show_image('eroded', image, enable_showing)

    # обрезаем углы
    kernel_size = int(angle_radius * ppm) * 2
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)),
                             iterations=smoothing)
    show_image('opened', image, enable_showing)

    # строим путь
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    field_edge = np.array(contours).reshape((-1, 2))
    field_edge[-1] = field_edge[0]
    path_simple = rdp(field_edge, epsilon=rdp_epsilon)

    # визуализируем
    path = np.zeros(image.shape, np.uint8)
    for i in range(len(field_edge) - 1):
        p1 = field_edge[i]
        p2 = field_edge[i + 1]
        cv2.line(path, p1, p2, 128, ppm * 12)
    # доп линия
    for i in range(len(field_edge) - 1):
        p1 = field_edge[i]
        p2 = field_edge[i + 1]
        cv2.line(path, p1, p2, 255, 1)
    show_image('path', path, enable_showing)

    return path, field_edge, path_simple


def translate_coords(pixel_coords, convertation_table):
    geo_coords = []
    for point in pixel_coords:
        geo_coords.append(np.array(convertation_table[point[1]][point[0]]))
    return np.array(geo_coords)


def path_callback(ppm, path, obstacle_size=20.0, angle_radius=10.0, smoothing=1, rdp_epsilon=3.0,
                  start_point=(26.973208407171384, 53.21215603723456)):
    # выгрузка точек из файлов
    points, rect = read_points(path=path, bbox=True)

    # создание изображения и таблицы конвертации
    image, convertation_table = create_image(points, rect, ppm=ppm)

    # поиск пути объезда по периметру
    path_image, path, path_simple = get_perimeter_path(image, ppm, obstacle_size, angle_radius, smoothing, rdp_epsilon)

    # вывод границ поля и полученного пути на экран
    # cv2.imshow('original_field_edge', image)
    # cv2.imshow('path', path_image + image)
    # cv2.waitKey()
    return path, path_simple, convertation_table


class Line:
    def __init__(self, p1, p2):
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        dx = x1 - x2
        dy = y1 - y2
        self.length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        self.ang = atan2(y1 - y2, x1 - x2)
        self.k = dy / dx if dx != 0 else 10e5
        self.b = y1 - self.k * x1
        self.p1, self.p2 = p1, p2

    def coord(self):
        return self.p1, self.p2


def hatching_planning(points):
    tree = []
    lines = {}
    lines['done'] = []
    lines['undone'] = []
    for i in range(len(points) - 1):
        lines['undone'].append(Line(points[i], points[i + 1]))
    tree = split_into_fields(lines['undone'], points)

    # 1 and 5
    # cv2.contourArea(a['done'][0]), cv2.contourArea(a['points'][0])

    ############## vis ####################

    img1 = np.zeros((np.amax(points, axis=0) + np.amin(points, axis=0))[::-1], np.uint8)
    img2 = np.zeros((np.amax(points, axis=0) + np.amin(points, axis=0))[::-1], np.uint8)
    img3 = np.zeros((np.amax(points, axis=0) + np.amin(points, axis=0))[::-1], np.uint8)

    for point in points:
        cv2.line(img1, point, point, 255, 5)
    for point in tree[1]['done'][0]:
        cv2.line(img2, point, point, 255, 5)
    for point in tree[1]['points'][0]:
        cv2.line(img3, point, point, 255, 5)
    cv2.imshow('1', img1)
    cv2.imshow('2', img2)
    cv2.imshow('3', img3)
    cv2.waitKey()

    #######################################

    ## дописать рекурсию
    # for subline in tree:
    #     subline['undone'] = []
    #     if (len(subline['points']) != 0):
    #         for i in range(len(subline['points'][0]) - 1):
    #             subline['undone'].append(Line(subline['points'][0][i], subline['points'][0][i + 1]))
    #         subline['tree'] = split_into_fields(subline['undone'], subline['points'][0])
    #
    # print(tree)


def split_into_fields(field, points):
    if (len(points) == 0):
        return []
    all_square = cv2.contourArea(points)

    img = np.zeros((np.amax(points, axis=0) + np.amin(points, axis=0))[::-1], np.uint8)
    for i in range(len(points) - 1):
        cv2.line(img, (points[i][0], points[i][1]), (points[i + 1][0], points[i + 1][1]), 15, 1)
    toReturn = []
    for line in sorted(field, key=lambda x: x.length)[::-1]:
        b1, b2, center, square = get_parallel_borders(field, line.k, line.b, points)
        image = np.zeros((np.amax(points, axis=0) + np.amin(points, axis=0))[::-1], np.uint8)
        cv2.line(image, (0, int(b1)), (10000, int(line.k * 10000 + b1)), 15, 1)
        cv2.line(image, (0, int(b2)), (10000, int(line.k * 10000 + b2)), 15, 1)
        image = img + image
        image = (image // 15) * 15
        cv2.floodFill(image, None, center, 255)
        full_field = img.copy()
        cv2.floodFill(full_field, None, center, 255)
        if (np.count_nonzero((image // 10) * 10) / all_square > 0.1):
            diff = full_field - image
            image = cv2.morphologyEx(image, cv2.MORPH_OPEN,
                                     cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
            diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN,
                                    cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
            image = cv2.morphologyEx(image, cv2.MORPH_CLOSE,
                                     cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
            diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE,
                                    cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))

            done_edge = np.array(cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]).reshape(
                (-1, 2))
            done_edge = rdp(done_edge, epsilon=5)
            done_square = cv2.contourArea(done_edge)
            # cv2.imshow('diff',diff)
            # cv2.waitKey()
            undone_edge = np.array(cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0])
            lines = {}
            lines['done'] = [done_edge]
            if (done_square / all_square > 0.9):
                lines['points'] = []
            else:
                lines['points'] = [undone_edge]
            toReturn.append(lines)
    return toReturn


def check_crossing(k1, b1, line):
    k2 = line.k
    b2 = line.b
    # k1*x + b1 = k2*x + b2
    # b1 - b2 = (k2 - k1) * x
    # x = (b1 - b2) / (k2 - k1)
    # y = k1 * x + b1
    x = (b1 - b2) / (k2 - k1) if (k2 - k1) != 0 else 10e5
    y = k1 * x + b1
    trsh = 3

    if (x + trsh >= min(line.p1[0], line.p2[0]) and x - trsh <= max(line.p1[0], line.p2[0]) and y + trsh >= min(
            line.p1[1],
            line.p2[1]) and y - trsh <= max(
        line.p1[1], line.p2[1])):
        return True, [round(x), round(y)]
    else:
        return False, [0, 0]


def get_crossings(lines, k, b):
    crossing_points = []
    crossed_lines = []
    for i in range(len(lines)):
        result, coord = check_crossing(k, b, lines[i])
        if (result):
            crossed_lines.append((i, coord))
            crossing_points.append(coord)
    return len(np.unique(crossing_points, axis=0)), crossed_lines


def get_parallel_borders(lines, k, b, points):
    b_and_crossing = []

    for point in np.unique(points, axis=0):
        b_new = point[1] - k * point[0]
        b_and_crossing.append([b_new - b, get_crossings(lines, k, b_new)])
    b_and_crossing.sort(key=lambda x: x[0])

    for i in range(len(b_and_crossing)):
        if (b_and_crossing[i][0] == 0.0):
            middle_index = i
            right_index = len(b_and_crossing) - 1
            left_index = 0
            break
    for i in range(middle_index + 1, len(b_and_crossing)):
        if (b_and_crossing[i][1][0] >= 3):
            right_index = i
            break
    for i in range(middle_index, -1, -1):
        if (b_and_crossing[i][1][0] >= 3):
            left_index = i
            break
    # print('left: ', b_and_crossing[left_index])
    # print('right: ', b_and_crossing[right_index])
    max_x = max((max(b_and_crossing[left_index][1][1], key=lambda x: x[1][0]))[1][0],
                (max(b_and_crossing[right_index][1][1], key=lambda x: x[1][0]))[1][0])
    min_x = min((min(b_and_crossing[left_index][1][1], key=lambda x: x[1][0]))[1][0],
                (min(b_and_crossing[right_index][1][1], key=lambda x: x[1][0]))[1][0])
    max_y = max((max(b_and_crossing[left_index][1][1], key=lambda x: x[1][1]))[1][1],
                (max(b_and_crossing[right_index][1][1], key=lambda x: x[1][1]))[1][1])
    min_y = min((min(b_and_crossing[left_index][1][1], key=lambda x: x[1][1]))[1][1],
                (min(b_and_crossing[right_index][1][1], key=lambda x: x[1][1]))[1][1])

    return b_and_crossing[left_index][0] + b, b_and_crossing[right_index][0] + b, (
        int((max_x + min_x) / 2), int((max_y + min_y) / 2)), (max_x - min_x) * (max_y - min_y)
