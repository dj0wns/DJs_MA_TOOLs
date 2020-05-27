from maze_lib.maze import Maze


#maze = {
#  "border_walls": set(<OuterEdge>),
#  "maze_walls": set(<InnerEdge>),
#  "start": <PathNode.id>,
#  "finish": <PathNode.id>,
#  "path_nodes": {
#    <PathNode.id>: {
#      "node": <Node>,
#      "map_coordinates": (0.0, 0.0),
#      "is_leaf_node": True,
#      "dist_from_start": 1,
#      "dist_from_finish": 1,
#    }
#  }
#}
def generate_maze_graph(length, width, path_thickness, mesh_width, tesselation_name, routing):
  maze = Maze(length, width, path_thickness, mesh_width, tesselation_name, routing)
  # TODO: calculate map coordinates
  # TODO: select start node
  # TODO: select finish node
  # TODO: assign IDs to path nodes
  # TODO: run algorithm to calculate distance from start, distance from finish, and whether it's a leaf

  maze_dict = {
    "border_walls": maze.border_walls,
    "maze_walls": maze.maze_walls,
  }

  return maze_dict
