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
class point:
    def __init__(self, p, sim):
        self.p = p
        self.x = p[0]
        self.y = p[1]
        #self.x = int(round((p[0] - sim.min_x) / sim.xw_step))
        #self.y = int(round((p[1] - sim.min_y) / sim.yh_step))
        self.p = (self.x, self.y)
def check_crossing(k1, b1, line):
    k2 = line.k
    b2 = line.b
    x = (b1 - b2) / (k2 - k1)
    y = k1 * x + b1
    if (x >= min(line.p1[0], line.p2[0]) and x <= max(line.p1[0], line.p2[0]) and y >= min(line.p1[1], line.p2[1]) and y >= max(line.p1[1], line.p2[1])):
        return True
    else:
        return False
def points2area(points):
    contour = np.array([i for i in points])
    return cv2.contourArea(contour)
#w = shapefile.Writer(shapeType=1)
def write_shp(track):
    w = shapefile.Writer("shapefiles/test/")
    #w.poly(parts=[track]) 
    #w.field('FIRST_FLD','C','40') 
    #w.field('SECOND_FLD','C','40') 
    #w.record('First','Polygon') 
    #w.save('/polygon')
    w.field('name', 'C')
    w.multipoint(track) 
    w.record('multipoint1')
    w.close()

if __name__ == "__main__":
    
    sf = shapefile.Reader("Trimble/Pole")
    s = sf.shape(0)
    print(sf.fields)
    points = s.points
    sim = agro_sim(3, sf.bbox, 6, 5)
    sim.draw_contour(points, 1)
    import main
    track = rdp(main.geo_coords, epsilon = 1 / (4 * 10e3))
    for i in range(len(track) - 1):
        k = 0
        while not sim.step_tractor(track[i], track[i + 1], k, True):
            sim.show(1)
            k += 1
    sim.show(1)
    



    
    track =[[809, 19],
    [683, 84],
    [546, 43],
    [84, 272],
    [368, 356],
    [772, 425],
    [827, 412],
    [972, 94],
    [810, 19]]
    write_shp(track)
    
    points = []
    for i in track:
        points.append(point(i, sim))
    
    lines_xy = [[]]
    for i in range(len(track) - 1):
        p1, p2 = track[i], track[i + 1]
        x1 = int(round((p1[0] - sim.min_x) / sim.xw_step))
        y1 = int(round((p1[1] - sim.min_y) / sim.yh_step))
        x2 = int(round((p2[0] - sim.min_x) / sim.xw_step))
        y2 = int(round((p2[1] - sim.min_y) / sim.yh_step))
        #print(x1, y1, x2, y2)
        lines_xy[0].append(Line((x1, y1), (x2, y2)))
    
    
    for i in range(len(track) - 1):
        p1, p2 = track[i], track[i + 1]
        lines_xy[0].append(Line(p1, p2))
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
    
    corners = \
    [[809, 19],
    [683, 84],
    [546, 43],
    [84, 272],
    [368, 356],
    [772, 425],
    [827, 412],
    [972, 94],
    [810, 19]]
    ppm = 10
    tool = 11.9
    field = np.zeros((150 * ppm, 150 * ppm), np.uint8)
    for i in range(len(corners)):
        cv2.circle(field, corners[i], 2, 255, -1)
    
    corners.append(corners[0])
    lines = []
    for i in range(len(corners) - 1):
        p1, p2 = corners[i], corners[i + 1]
        lines.append(Line(p1, p2))
    
    #lines_sorted = lines.copy()
    #lines_sorted.sort(key=lambda x:x.length)[::-1]
    bottom_line = lines[0]
    for i in lines:
        if i.length > bottom_line.length:
            bottom_line = i
    print("ff", bottom_line.ang)
    for i in lines:
        cv2.line(field, i.coord()[0], i.coord()[1], 40, 2)
    cv2.line(field, bottom_line.coord()[0], bottom_line.coord()[1], 255, 2)
    cv2.imshow("Line", field)
    cv2.waitKey(0)
    theta = -bottom_line.ang

    rot = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
    rot_corners = corners.copy()
    for i in range(len(rot_corners)):
        rot_corners[i] = np.dot(rot, rot_corners[i]).astype(int)
    #bottom_line_rot = Line(np.dot(rot, bottom_line.coord[0]).astype(int), np.dot(rot, bottom_line.coord[1]).astype(int))


    #rotated already
    rotated_field = np.zeros((150 * ppm, 150 * ppm), np.uint8)
    rot_lines = []
    for i in range(len(rot_corners) - 1):
        p1, p2 = rot_corners[i], rot_corners[i + 1]
        rot_lines.append(Line(p1, p2))
    #lines_sorted = lines.copy()
    #lines_sorted.sort(key=lambda x:x.length)[::-1]
    rot_bottom_line = rot_lines[0]
    b_l_index = 0
    k  = 0
    for i in rot_lines:
        if i.length > rot_bottom_line.length:
            rot_bottom_line = i
            b_l_index = k
        k += 1

    #print("ff", bottom_line.ang)
    for i in rot_lines:
        cv2.line(rotated_field, i.coord()[0] + 100, i.coord()[1] + 100, 40, 2)
    cv2.line(rotated_field, rot_bottom_line.coord()[0] + 100, rot_bottom_line.coord()[1] + 100, 255, 2)
    P0 = rot_bottom_line.coord()[0]
    cv2.circle(rotated_field, P0 + 100, 5, 255, -1)
    track = []
    offset = 0
    r_i = 1
    l_i = 1
    flag = True
    while True:
        line_1 = rot_lines[b_l_index - r_i]
        line_2 = rot_lines[b_l_index + l_i]
        y = P0[1] + round(tool / 2 * ppm + offset * (tool * ppm))
        try:
            while y > rot_lines[b_l_index + l_i].coord()[1][1]:
                l_i += 1
            while y > rot_lines[b_l_index - r_i].coord()[0][1]:
                r_i += 1
        except:
            break
            
        line_1 = rot_lines[b_l_index - r_i]
        line_2 = rot_lines[b_l_index + l_i]
        a = round((y - line_1.b) / line_1.k)
        b = round((y - line_2.b) / line_2.k)
        if flag:
            track.append((a, y))
        track.append((b, y))
        if not flag:
            track.append((a, y))
        flag = not flag
        cv2.line(rotated_field, (a + 100, y + 100), (b + 100, y + 100), 255, 2)
        cv2.circle(rotated_field, (a + 100, y + 100), 5, 40, -1)
        cv2.circle(rotated_field, (b + 100, y + 100), 5, 40, -1)
        offset += 1
        if offset == 10:
            break
        
        cv2.imshow("Line", rotated_field)
        cv2.waitKey(0)
    print(track)