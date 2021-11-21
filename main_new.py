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

    #draw small red line wth big green line 
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

        #perpendicular
        a, b = round(self.tool * sin(angle)), round(self.tool * cos(angle))
        #print(self.tool)
        cv2.line(self.filled, (current_point[0] + a, current_point[1] - b), (current_point[0] - a, current_point[1] + b), (0, 255, 0), 2, cv2.LINE_8)
  
        if current_point == (x2, y2):
            cv2.circle(self.filled, (x2, y2), self.tool + 1, (0, 255, 0), -1)
            return 1
        else:
            return 0
    
        
    def show(self, delay = None, debug = False):
        if debug:
            cv2.imshow("Field", self.field)
            cv2.imshow("Filled", self.filled)
            cv2.imshow("track", self.track)
        else:
            

            cv2.resize(self.field + self.filled + self.track, (1080, 1920), interpolation = cv2.INTER_AREA)
            cv2.imshow("Agro", self.field + self.filled + self.track)

        if not delay is None:
            cv2.waitKey(delay)

def translate_coords(pixel_coords, convertation_table):
    geo_coords = []
    for point in pixel_coords:
        geo_coords.append(np.array(convertation_table[point[1]][point[0]]))
    return np.array(geo_coords)

if __name__ == "__main__":
    
    from main import path_callback
    from main import get_perimeter_part
    from shape_writer import write_shp
    #from pattern import relocation

    track = []

    # масштаб (пикселей на метр)
    # влияет на точность
    ppm = 2
    # параметры для поиска пути объезда по периметру (крутилки)
    # все числа float, кроме smoothing
    
    # радиус поворота в метрах [0; inf)
    angle_radius = 6.0
    # степень сглаживания [1; inf)
    smoothing = 1
    # степень упрощения пути алгоритмом Рамера-Дугласа-Пекера (0; inf)
    rdp_epsilon = 1

    # file path list
    fields_path_dir_list = ["Trimble/Pole",
                            "Moscow/Moscow",
                            "Cherep/Cherep",
                            "Ukraine/Ukraine",
                            "Belarus/Belarus"]

    # точка, рядом с которой должен начинаться путь
    start_point_field_list =   [(26.97198642737419,53.21268092272585),
                                (37.55972921848297,55.837689974599186),
                                (37.85521745681763,59.18315110901265),
                                (34.83020335435867,49.54095106379548),
                                (27.375474125146866, 53.26050256167628)]                        

    # размеры используемого устройства
    tool_size_list = [5, 12]

    # индекс рабочего поля (0 - поле агрокода, 1 - поле в РХТУ им.Тимирязева, 2 - поле в Череповце, 3 - поле в/на Украине, 4 - поле в Беларуси)
    place_id = 0

    # индекс рабочего инструмента (0 - сеялка, 1 - полив)
    tool_id = 0

    # расстояние между центром робота и границей поля aka радиус сеялки в метрах [0; inf)
    obstacle_size = tool_size_list[tool_id] + 1

    start_point = start_point_field_list[place_id]
    
    path_dir = fields_path_dir_list[place_id]

    
    # зависит от используемого инструмента
    if tool_id == 0:
        borders = 13
    else: 
        borders = 1

    
    sf = shapefile.Reader(path_dir)
    s = sf.shape(0)
    points = s.points
    sim = agro_sim(3, sf.bbox, tool_size_list[tool_id], 5)
    sim.draw_contour(points, 1)

    for border in range(0,borders):
        
        
        obstacle = (obstacle_size + (tool_size_list[tool_id]*1.5*border))
        print("obstacle - ", obstacle)

        image, path_image, geo_coords, convertation_table = path_callback(ppm, path_dir, obstacle, angle_radius, smoothing, rdp_epsilon, start_point)   
        track += list(geo_coords)
        
        if tool_id == 0:
            x1 = track[-2][0] + (track[-1][0]-track[-2][0])/2
            y1 = track[-2][1] + (track[-1][1]-track[-2][1])/2

            track.pop()
            track.append([x1,y1])

    if tool_id == 0:
        track.pop()
        track.pop()   
        write_shp(track, "./json/Pole_first.json")
    else:
        write_shp(track, "./json/Pole_second.json")
    
    for i in range(len(track) - 1):
        k = 0
        while not sim.step_tractor(track[i], track[i+1], k, True):
            sim.show(1)
            k += 1

    track.append( [start_point_field_list[place_id]])

    get_perimeter_part(image, ppm, angle_radius=5, smoothing=1, enable_showing=False)
    sim.show(1)
    cv2.waitKey(0)

