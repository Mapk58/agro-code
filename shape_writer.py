from os import path
import shapefile
import json
import numpy as np

#w = shapefile.Writer(shapeType=1)
def write_shp(track = [], path = './json/Pole_second.json'):

    json_data = {"type":"GeometryCollection", "geometries": [
{"type":"Polygon","coordinates":[]}
]}
    
    json_data["geometries"][0]["coordinates"] = [np.array(track).tolist()]
    
    data = json_data['geometries'][0]['coordinates'][0]

    for item in range(0,len(data)):
        float_mem = data[item][0]
        data[item][0] = data[item][1]
        data[item][1] = float_mem

    json_data["geometries"][0]["coordinates"] = [data]

    print(json_data["geometries"][0]["coordinates"])
    with open(path, 'w') as outfile:
        json.dump(json_data, outfile)
    