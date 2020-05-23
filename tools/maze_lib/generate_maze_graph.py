from maze_lib.maze import Maze


#maze = {
#  "outer_edges": set(<OuterEdge>),
#  "inner_edges": set(<InnerEdge>),
#  "start": (0.0,0.0),
#  "finish": (0.0,0.0),
#  "path_nodes": {
#    <PathNode.id>: {
#      "node": <Node>,
#      "is_leaf_node": True,
#      "dist_from_start": 1,
#      "dist_from_finish": 1,
#    }
#  }
#}
def generate_maze_graph(length, width, path_thickness, mesh_width, tesselation_name, routing):
  maze = Maze(length, width, path_thickness, mesh_width, tesselation_name, routing)

  maze_dict = {
    "outer_edges": maze.border_walls,
    "inner_edges": maze.maze_walls,
  }

  return maze_dict
