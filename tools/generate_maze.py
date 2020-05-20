import argparse
import os

fpath=os.path.realpath(__file__)
py_path=os.path.dirname(fpath)


def execute(length, width, center_x, center_y, maze_tesselation, mesh_name, mesh_width, path_thickness, routing, output):
  init_shape_game_data_list = {} 
  if mesh_name is None:
    mesh_name = "goshcrate02"
  if mesh_width is None:
    mesh_width = 1.
  if path_thickness is None:
    path_thickness = 1.
  if maze_tesslation.lower() == "orthogonal":
    None
    #build graph
    #generate walls
    #generate enemies
  else:
    print ("Unrecognized maze tesselation type")
    return False

  #output to folder

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Rebuild a CSV file")
  routing_style = parser.add_mutually_exclusive_group()
  routing_style.add_argument("-p", "--perfect", help="A maze with exactly 1 solution [default]", action='store_const', dest="routing", const='perfect', default='perfect')
  routing_style.add_argument("-b", "--braid", help="A maze with no dead ends - it loops back on itself", action='store_const', dest="routing", const='braid')
  routing_style.add_argument("-u", "--unicursal", help="A maze with exactly 1 path", action='store_const', dest="routing", const='unicursal')
  parser.add_argument("-x", "--center-x", help="x-value of the maze center", default=0)
  parser.add_argument("-y", "--center-y", help="x-value of the maze center", default=0)
  parser.add_argument("-t", "--maze-tesselation", help="orthogonal: a simple rectangular maze\nOther maze types to come!", default="orthogonal")
  expertArgs = parser.add_argument_group('expert arguments - don\'t use these unless you know what you are doing')
  expertArgs.add_argument("--mesh-name", help="Name of mesh you want to use, using the default mesh is recommended")
  expertArgs.add_argument("--mesh-width", help="width of the mesh used for the walls")
  expertArgs.add_argument("--path-thickness", help="thickness of the path used for the maze")
  requiredNamed = parser.add_argument_group('required named arguments')
  requiredNamed.add_argument("-l", "--length", help="Length of Maze in game units", required=True)
  requiredNamed.add_argument("-w", "--width", help="Width of Maze in game units", required=True)
  parser.add_argument("output", type=str, help="Output folder")
  args = parser.parse_args()
  execute(args.length, args.width, args.center_x, args.center_y, args.maze_type, args.routing, args.mesh_name, args.mesh_width, args.path_thickness, args.output)
