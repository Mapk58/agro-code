import shapefile
import cv2
import numpy as np
from math import *
from vincenty import vincenty
from rdp import rdp
class agro_sim():
    def __init__(self, ppm, bbox, tool, radius) -> None:
        self.tool = ppm * tool
        self.rect = bbox
        borders = 2 * 10e-6
        min_x, max_x = self.rect[0], self.rect[2]
        min_y, max_y = self.rect[1], self.rect[3]
        self.min_x, self.min_y, self.max_x, self.max_y = min_x, min_y, max_x, max_y
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
        self.xw_step = (max_x - min_x) / (w_average * ppm)
        self.yh_step = (max_y - min_y) / (h_average * ppm)

        self.size = (int(h_average * ppm + 1), int(w_average * ppm + 1))

        self.field = np.zeros((self.size[0], self.size[1], 3), np.uint8)
        self.track = np.zeros_like(self.field)
        self.filled = np.zeros_like(self.field)
        # таблица совместимости пиксель-координата
        self.p2c = np.array(
            [np.array([(min_x + self.xw_step * i, min_y + self.yh_step * j) for i in range(w_average * ppm)]) for j in
            range(h_average * ppm)])


    def draw_contour(self, points, width = 1):
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            x1 = int(round((p1[0] - self.min_x) / self.xw_step))
            y1 = int(round((p1[1] - self.min_y) / self.yh_step))
            x2 = int(round((p2[0] - self.min_x) / self.xw_step))
            y2 = int(round((p2[1] - self.min_y) / self.yh_step))
            cv2.line(self.field, (x1, y1), (x2, y2), (0, 0, 255), width)
        return self.field

    def step_tractor(self, origin_point, desired_point, iter, not_end):
        x1 = int(round((origin_point[0] - self.min_x) / self.xw_step))
        y1 = int(round((origin_point[1] - self.min_y) / self.yh_step))
        x2 = int(round((desired_point[0] - self.min_x) / self.xw_step))
        y2 = int(round((desired_point[1] - self.min_y) / self.yh_step))
        angle = atan2(y2 - y1, x2 - x1)
        
        #cv2.circle(self.field, (x1, y1), 2, (255,0,0), 2)
        #cv2.circle(self.field, (x2, y2), 2, (0,255,0), 2)
        cv2.line(self.track, (x1, y1), (x2, y2), (0, 0, 255), 1)
        current_point = (round(iter * cos(angle) + x1), round(iter * sin(angle) + y1))
        #cv2.circle(mask, (current_point[0], current_point[1]), 1, (0, 0, 255), 1)
        a, b = round(self.tool * sin(angle)), round(self.tool * cos(angle))
        cv2.line(self.filled, (current_point[0] + a, current_point[1] - b), (current_point[0] - a, current_point[1] + b), (0, 255, 0), 2, cv2.LINE_8)
        if current_point == (x2, y2):
            cv2.circle(self.filled, (x2, y2), round(self.tool + 1), (0, 255, 0), -1)
            return 1
        else:
            return 0
    
        
    def show(self, delay = None, debug = False):
        if debug:
            cv2.imshow("Field", self.field)
            cv2.imshow("Filled", self.filled)
            cv2.imshow("track", self.track)
        else:
            cv2.imshow("Agro", self.field + self.filled + self.track)
        if not delay is None:
            cv2.waitKey(delay)

def translate_coords(pixel_coords, convertation_table):
    geo_coords = []
    for point in pixel_coords:
        geo_coords.append(np.array(convertation_table[point[1]][point[0]]))
    return np.array(geo_coords)
class line:
    def __init__(self, p1, p2):
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        self.length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        self.ang = atan2(y1 - y2, x1 - x2)
        #self.ang = atan2(x2 - x1, y2 - y1)
        self.p1, self.p2 = p1, p2
    def coord(self):
        return self.p1, self.p2
class point:
    def __init__(self, p, sim):
        self.p = p
        self.x = p[0]
        self.y = p[1]
        #self.x = int(round((p[0] - sim.min_x) / sim.xw_step))
        #self.y = int(round((p[1] - sim.min_y) / sim.yh_step))
        self.p = (self.x, self.y)
if __name__ == "__main__":
    sf = shapefile.Reader("Trimble/Pole")
    s = sf.shape(0)
    points = s.points
    sim = agro_sim(3, sf.bbox, 6, 5)
    sim.draw_contour(points, 1)
    import main
    track = rdp(main.geo_coords, epsilon = 1 / (4 * 10e3))
    for i in range(len(track) - 1):
        k = 0
        while not sim.step_tractor(track[i], track[i + 1], k, True):
            #sim.show(1)
            k += 1
    #sim.show(1)
    '''
    contours = cv2.findContours(cv2.split(sim.track)[2], cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    for i in contours[0]:
        print(i)
    '''



    
    track =[[809, 19],
    [683, 84],
    [546, 43],
    [84, 272],
    [368, 356],
    [772, 425],
    [827, 412],
    [972, 94],
    [810, 19]]
    
    points = []
    for i in track:
        points.append(point(i, sim))
    
    lines_xy = [[]]
    '''
    for i in range(len(track) - 1):
        p1, p2 = track[i], track[i + 1]
        x1 = int(round((p1[0] - sim.min_x) / sim.xw_step))
        y1 = int(round((p1[1] - sim.min_y) / sim.yh_step))
        x2 = int(round((p2[0] - sim.min_x) / sim.xw_step))
        y2 = int(round((p2[1] - sim.min_y) / sim.yh_step))
        #print(x1, y1, x2, y2)
        lines_xy[0].append(line((x1, y1), (x2, y2)))
    '''
    for i in range(len(track) - 1):
        p1, p2 = track[i], track[i + 1]
        lines_xy[0].append(line(p1, p2))
    lines_xy[0].sort(key=lambda x:x.length)
    lines_xy[0] = lines_xy[0][::-1]
    
    contour = np.array([i.coord()[0] for i in lines_xy[0]])
    image = np.zeros_like(sim.field)
    z = 1
    cv2.line(image, lines_xy[0][z].coord()[0], lines_xy[0][z].coord()[1], (0, 0, 255), 2)

    points.sort(key=lambda x:(x.p[1] - round(x.p[0] * tan(lines_xy[0][z].ang))))
    for i in range(len(points)):
       print(points[i].p, points[i].p[1] - round(points[i].p[0] * tan(lines_xy[0][z].ang)))
       cv2.circle(image, points[i].p, 2, (0, 255, 0), -1)
       cv2.imshow("Line", image)
       cv2.waitKey(0)
    cv2.imshow("Line", image)
    area = cv2.contourArea(contour)

    cv2.waitKey(0)