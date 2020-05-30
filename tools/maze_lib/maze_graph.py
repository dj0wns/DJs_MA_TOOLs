from maze_lib.maze import Maze
import random


#maze = {
#  "border_walls": set(<OuterEdge>),
#  "maze_walls": set(<InnerEdge>),
#  "start": <Node.id>,
#  "finish": <Node.id>,
#  "nodes": {
#    <Node.id>: {
#      "node": <Node>,
#      "is_leaf_node": True,
#      "dist_from_start": 1,
#      "dist_from_finish": 1,
#    }
#  }
#}
def generate_maze_graph(length, width, path_thickness, mesh_width, tesselation_name, routing):
  maze = Maze(length, width, path_thickness, mesh_width, tesselation_name, routing)

  nodes = maze.tesselation.nodes.values()

  start_node = random.choice(nodes)
  finish_node = random.choice(nodes)

  # TODO: run algorithm to calculate distance from start, distance from finish, and whether it's a leaf
  nodes_dict = {}
  for node in nodes:
    nodes_dict[node.id] = {
      "node": node,
    }

  maze_dict = {
    "border_walls": maze.border_walls,
    "maze_walls": maze.maze_walls,
    "start": start_node.id,
    "finish": finish_node.id,
    "nodes": nodes_dict,
  }

  return maze_dict
