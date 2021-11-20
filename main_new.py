import shapefile
import cv2
import numpy as np
from math import *
from vincenty import vincenty

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

    def step_tractor(self, origin_point, desired_point, iter, ):
        x1 = int(round((origin_point[0] - self.min_x) / self.xw_step))
        y1 = int(round((origin_point[1] - self.min_y) / self.yh_step))
        x2 = int(round((desired_point[0] - self.min_x) / self.xw_step))
        y2 = int(round((desired_point[1] - self.min_y) / self.yh_step))
        angle = atan2(y2 - y1, x2 - x1)
        
        #cv2.circle(self.field, (x1, y1), 2, (255,0,0), 2)
        #cv2.circle(self.field, (x2, y2), 2, (0,255,0), 2)
        cv2.line(self.field, (x1, y1), (x2, y2), (0, 0, 255), 1)
        current_point = (round(iter * cos(angle) + x1), round(iter * sin(angle) + y1))
        cv2.circle(self.field, (current_point[0], current_point[1]), 1, (0, 0, 255), 1)
        a, b = round(self.tool * sin(angle)), round(self.tool * cos(angle))
        cv2.line(self.field, (current_point[0] + a, current_point[1] - b), (current_point[0] - a, current_point[1] + b), (0, 255, 0), 2, cv2.LINE_8)
        return (1 if current_point == (x2, y2) else 0)
    def corner(self, prev_point, origin_point, desired_point):
        x0 = int(round((prev_point[0] - self.min_x) / self.xw_step))
        y0 = int(round((prev_point[1] - self.min_y) / self.yh_step))
        x1 = int(round((origin_point[0] - self.min_x) / self.xw_step))
        y1 = int(round((origin_point[1] - self.min_y) / self.yh_step))
        x2 = int(round((desired_point[0] - self.min_x) / self.xw_step))
        y2 = int(round((desired_point[1] - self.min_y) / self.yh_step))

    def show(self):
        cv2.imshow("Field", self.field)
        cv2.waitKey(5)

if __name__ == "__main__":
    sf = shapefile.Reader("Trimble/Pole")
    s = sf.shape(0)
    points = s.points
    sim = agro_sim(5, sf.bbox, 6, 5)
    sim.draw_contour(points, 1)
    o_point = (26.973251, 53.212172)
    d_point = (26.974555, 53.212870)
    from track import track
    for i in range(len(track) - 1):
        k = 0
        while not sim.step_tractor(track[i], track[i+1], k):
            sim.show()
            k += 1
    cv2.waitKey(0)