import sys
import os
import math
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from lib import init_classes, ma_util

def create_mil_of_type(x, y, z, bottype, weapon_name, secondary_name, has_shield):
  init = ma_util.default_init()
  init.data['shape_type'] = "FWORLD_SHAPETYPE_POINT"
  init.data['Position_X'] = x
  init.data['Position_Y'] = y 
  init.data['Position_Z'] = z
  shape = ma_util.default_point_shape()
  gamedata = ma_util.default_gamedata()
  ma_util.add_table_to_gamedata(gamedata, "name", ["start01"], ["STRING"])
  init_shape_game_data_list.append([init, shape, gamedata])



def create_shape_at_center_of_2_points(x_0, z_0, x_1, z_1, center_x, center_z):
    wall_center_x = (x_0 + center_x + x_1 + center_x) / 2.
    wall_center_z = (z_0 + center_z + z_1 + center_z) / 2.
    #build a shape at these coords
    init = ma_util.default_init()
    shape = ma_util.default_mesh_shape()
    init.data['Position_X'] = wall_center_x
    init.data['Position_Y'] = 0 
    init.data['Position_Z'] = wall_center_z

    #figure out rotation
    front_vector_x = x_1 - x_0
    front_vector_z = z_1 - z_0
    magnitude = math.sqrt(front_vector_x ** 2 + front_vector_z ** 2)
    unit_vector_x = front_vector_x / magnitude
    unit_vector_z = front_vector_z / magnitude

    init.data['Front_X'] = unit_vector_x
    init.data['Front_Y'] = 0.0
    init.data['Front_Z'] = unit_vector_z
    
    init.data['Right_X'] = init.data["Front_Z"]
    init.data['Right_Y'] = 0.0
    init.data['Right_Z'] = -init.data["Front_X"] if -init.data["Front_X"] != 0.0 else 0.0
    
    init.data['Up_X'] = 0.0
    init.data['Up_Y'] = 1.0
    init.data['Up_Z'] = 0.0

    return init, shape, None

def create_shape_at_point(x_0, z_0, center_x, center_z):
    wall_center_x = x_0 + center_x
    wall_center_z = z_0 + center_z
    #build a shape at these coords
    init = ma_util.default_init()
    shape = ma_util.default_mesh_shape()
    init.data['Position_X'] = wall_center_x
    init.data['Position_Y'] = 0 
    init.data['Position_Z'] = wall_center_z

    #TODO needs another variable for rotation
    init.data['Front_X'] = 1.0
    init.data['Front_Y'] = 0.0
    init.data['Front_Z'] = 0.0
    
    init.data['Right_X'] = 0.0
    init.data['Right_Y'] = 0.0
    init.data['Right_Z'] = -1.0
    
    init.data['Up_X'] = 0.0
    init.data['Up_Y'] = 1.0
    init.data['Up_Z'] = 0.0

    return init, shape, None


def graph_to_shapes(maze_dict, wall_mesh, node_mesh, center_x, center_z):
  init_shape_game_data_list = []
  #make start shape
  #TODO add positions
  init = ma_util.default_init()
  init.data['shape_type'] = "FWORLD_SHAPETYPE_POINT"
  shape = ma_util.default_point_shape()
  gamedata = ma_util.default_gamedata()
  ma_util.add_table_to_gamedata(gamedata, "name", ["start01"], ["STRING"])
  init_shape_game_data_list.append([init, shape, gamedata])

  #make end shape
  #TODO add positions
  init = ma_util.default_init()
  init.data['shape_type'] = "FWORLD_SHAPETYPE_POINT"
  shape = ma_util.default_point_shape()
  gamedata = ma_util.default_gamedata()
  ma_util.add_table_to_gamedata(gamedata, "name", ["end01"], ["STRING"])
  ma_util.add_table_to_gamedata(gamedata, "type", ["goodie"], ["STRING"])
  ma_util.add_table_to_gamedata(gamedata, "goodietype", ["secret chip"], ["STRING"])
  init_shape_game_data_list.append([init, shape, gamedata])
  

  #Add all wall nodes
  for wall_point in maze_dict["wall_points"]:
    init, shape, gamedata = \
        create_shape_at_point(wall_point.map_coordinates[0],
                              wall_point.map_coordinates[1],
                              center_x, center_z)
    shape.data['mesh'].mesh_name = node_mesh
    init_shape_game_data_list.append([init, shape, gamedata])

  for border_walls in maze_dict["border_walls"]:
    init, shape, gamedata = \
        create_shape_at_center_of_2_points(border_walls.wall_points[0].map_coordinates[0],
                                           border_walls.wall_points[0].map_coordinates[1],
                                           border_walls.wall_points[1].map_coordinates[0],
                                           border_walls.wall_points[1].map_coordinates[1],
                                           center_x, center_z)
    shape.data['mesh'].mesh_name = wall_mesh
    init_shape_game_data_list.append([init, shape, gamedata])
  
  for maze_walls in maze_dict["maze_walls"]:
    init, shape, gamedata = \
        create_shape_at_center_of_2_points(maze_walls.wall_points[0].map_coordinates[0],
                                           maze_walls.wall_points[0].map_coordinates[1],
                                           maze_walls.wall_points[1].map_coordinates[0],
                                           maze_walls.wall_points[1].map_coordinates[1],
                                           center_x, center_z)
    shape.data['mesh'].mesh_name = wall_mesh
    init_shape_game_data_list.append([init, shape, gamedata])


  return init_shape_game_data_list
  
