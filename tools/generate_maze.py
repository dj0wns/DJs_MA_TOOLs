import argparse
import os
from maze_lib import graph_to_shapes, maze_graph, output_shapes

fpath=os.path.realpath(__file__)
py_path=os.path.dirname(fpath)


def execute(length, width, center_x, center_z, tesselation, wall_mesh, node_mesh, mesh_width, path_thickness, routing, output):
  init_shape_game_data_list = {} 
  maze_dict = {}
  if wall_mesh is None:
    wall_mesh = "goss_cwall"
  if node_mesh is None:
    node_mesh = "gowcdiode01"
  if mesh_width is None:
    mesh_width = 2.
  if path_thickness is None:
    path_thickness = 35.
  if routing is None:
    routing = "perfect"
  if tesselation.lower() in ("orthogonal"):
    maze_dict = maze_graph.generate_maze_graph(float(length), float(width), path_thickness, mesh_width, tesselation, routing)
    # TODO by W
    #   call generate_maze()
    #     params:  length, width, path_thickness, mesh_width, tesselation,
    #              routing
    #     returns: maze graph
    # TODO by D
    #   call generate_walls_and_entities()
    #     params:  maze graph, center_x, center_y, rotation, difficulty
    #     returns: list of shapes
    init_shape_game_data_list = graph_to_shapes.graph_to_shapes(maze_dict, wall_mesh, node_mesh, center_x, center_z)
    # TODO
    #   call generate_shapes (in lib/ma_util.py) given list of shapes and output
    output_shapes.output_shapes(init_shape_game_data_list, output)

  else:
    print ("Unrecognized maze tesselation type")
    return False



if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Generate a maze")
  routing_style = parser.add_mutually_exclusive_group()
  routing_style.add_argument("-p", "--perfect", help="A maze with exactly 1 solution [default]", action='store_const', dest="routing", const='perfect', default='perfect')
  routing_style.add_argument("-b", "--braid", help="A maze with no dead ends - it loops back on itself", action='store_const', dest="routing", const='braid')
  routing_style.add_argument("-u", "--unicursal", help="A maze with exactly 1 path", action='store_const', dest="routing", const='unicursal')
  parser.add_argument("-x", "--center-x", help="x-value of the maze center", default=0)
  parser.add_argument("-z", "--center-z", help="z-value of the maze center", default=0)
  parser.add_argument("-t", "--tesselation", help="orthogonal: a simple rectangular maze\nOther maze types to come!", default="orthogonal")
  expertArgs = parser.add_argument_group('expert arguments - don\'t use these unless you know what you are doing')
  expertArgs.add_argument("--wall-mesh", help="Name of mesh you want to use for the walls of the maze")
  expertArgs.add_argument("--node-mesh", help="Name of mesh you want to use for the nodes of the maze")
  expertArgs.add_argument("--mesh-width", help="width of the mesh used for the walls")
  expertArgs.add_argument("--path-thickness", help="thickness of the path used for the maze")
  requiredNamed = parser.add_argument_group('required named arguments')
  requiredNamed.add_argument("-l", "--length", help="Length of Maze in game units", required=True)
  requiredNamed.add_argument("-w", "--width", help="Width of Maze in game units", required=True)
  parser.add_argument("output", type=str, help="Output folder")
  args = parser.parse_args()
  execute(args.length, args.width, args.center_x, args.center_z, args.tesselation, args.wall_mesh, args.node_mesh, args.mesh_width, args.path_thickness, args.routing, args.output)
