import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from lib import init_classes, ma_util

def graph_to_shapes(maze_dict, mesh_name, center_x, center_z):
  init_shape_game_data_list = []
  #make start shape
  #TODO add positions
  init = ma_util.default_init()
  init.data['shape_type'] = "FWORLD_SHAPETYPE_POINT"
  shape = ma_util.default_point_shape()
  gamedata = ma_util.default_gamedata()
  ma_util.add_table_to_gamedata(gamedata, "name", ["start01"], "STRING")
  init_shape_game_data_list.append([init, shape, gamedata])

  #make end shape
  #TODO add positions
  init = ma_util.default_init()
  init.data['shape_type'] = "FWORLD_SHAPETYPE_POINT"
  shape = ma_util.default_point_shape()
  gamedata = ma_util.default_gamedata()
  ma_util.add_table_to_gamedata(gamedata, "name", ["end01"], "STRING")
  ma_util.add_table_to_gamedata(gamedata, "type", ["goodie"], "STRING")
  ma_util.add_table_to_gamedata(gamedata, "goodietype", ["secret chip"], "STRING")
  init_shape_game_data_list.append([init, shape, gamedata])

  #for outer_edges in maze_dict["outer_edges"]:
  #  #make walls
  #  None
  #for inner_edge in maze_dict["inner_edges"]:
  #  #make walls
  #  None


  return init_shape_game_data_list
  
