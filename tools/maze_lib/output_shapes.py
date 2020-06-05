import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from lib import init_classes, ma_util

def output_shapes(init_shape_game_data_list, output):
  if not os.path.exists(output):
    os.mkdir(output)
  #output to folder
  index = 0
  for item in init_shape_game_data_list:
    name = "Maze-Object-" + str(index).zfill(4)
    init_object_file = open(os.path.join(output, name + "_init_object.json"), "w")
    init_object_file.write(ma_util.pretty_pickle_json(item[0]))
    init_object_file.close()

    if item[1] is not None:
      shape_file = open(os.path.join(output, name + "_shape.json"), "w")
      shape_file.write(ma_util.pretty_pickle_json(item[1]))
      shape_file.close()

    if item[2] is not None:
      gamedata_file = open(os.path.join(output, name + "_gamedata.json"), "w")
      gamedata_file.write(item[2].to_json())
      gamedata_file.close()
    index+=1

