import json
import sys

class MapInfo:
  def __init__(self, config_path):
    f = open(config_path, "r")
    json_file  = f.read()
    f.close()
    self.data = json.loads(json_file)
    #verify core keys are in the file
    if "file_name" not in self.data.keys():
      sys.exit("Missing file_name field")
    elif "level_name" not in self.data.keys():
      sys.exit("Missing level_name field")
    elif "x_dimension" not in self.data.keys():
      sys.exit("Missing x_dimension field")
    elif "y_dimension" not in self.data.keys():
      sys.exit("Missing y_dimension field")
    elif "x_center" not in self.data.keys():
      sys.exit("Missing x_center field")
    elif "y_center" not in self.data.keys():
      sys.exit("Missing y_center field")
    elif "image_pixels_per_map_x" not in self.data.keys():
      sys.exit("Missing x_scale field")
    elif "image_pixels_per_map_z" not in self.data.keys():
      sys.exit("Missing y_scale field")

    
