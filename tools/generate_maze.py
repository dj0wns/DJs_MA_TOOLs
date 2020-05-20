import argparse
import os

fpath=os.path.realpath(__file__)
py_path=os.path.dirname(fpath)


def execute(length, width, center_x, center_y, maze_type, mesh_name, output):
  None

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Rebuild a CSV file")
  requiredNamed = parser.add_argument_group('required named arguments')
  requiredNamed.add_argument("-l", "--length", help="Length of Maze", required=True)
  requiredNamed.add_argument("-w", "--width", help="Width of Maze", required=True)
  parser.add_argument("-x", "--center-x", help="x-value of the maze center", default=0)
  parser.add_argument("-y", "--center-y", help="x-value of the maze center", default=0)
  parser.add_argument("-t", "--maze-type", help="0: A block maze\nOther maze types to come!", default=0)
  parser.add_argument("-m", "--mesh-name", help="Name of mesh you want to use, using the default mesh is recommended")
  parser.add_argument("output", type=str, help="Output file")
  args = parser.parse_args()
  execute(args.length, args.width, args.center_x, args.center_y, args.maze_type, args.mesh_name, args.output)
