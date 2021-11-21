from path_planner import path_callback, translate_coords, set_start_point, hatching_planning

# масштаб (пикселей на метр)
ppm = 2
# расстояние между центром робота и границей поля aka радиус сеялки в метрах [0; inf)
obstacle_size = 6
# радиус поворота в метрах [0; inf)
angle_radius = 6.0
# степень сглаживания [1; inf)
smoothing = 1
# степень упрощения пути алгоритмом Рамера-Дугласа-Пекера (0; inf)
rdp_epsilon = 20

# точка, рядом с которой должен начинаться путь
start_point = (26.973208407171384, 53.21215603723456)

file_name = 'Pole'

path_coords, simple_path_coords, convertation_table = path_callback(ppm, "Trimble/" + file_name, obstacle_size, angle_radius,
                                                                    smoothing,
                                                                    rdp_epsilon,
                                                                    start_point)

# перевод координат пути в географические
geo_coords = translate_coords(path_coords, convertation_table)
# выбор стартовой точки, наиболее близкой к заданной
geo_coords = set_start_point(start_point, geo_coords)

hatching_planning(simple_path_coords)