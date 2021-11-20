import json
with open('tractor.json', 'rb') as infile:
    data = json.load(infile)
#print(type(data)) # dict
#print(data.keys()) # dict_keys(['events_data'])
#print('DATA ',data['features'][0]['geometry']['coordinates'][0][0]) # просмотр содержимого

data_list = data['features'][0]['geometry']['coordinates'][0]


for item in range(0,len(data_list)):
    float_mem = data_list[item][0]
    data_list[item][0] = data_list[item][1]
    data_list[item][1] = float_mem

print(data_list)