import os
import tkinter
import tkinter.filedialog
import json
import math
from enum import Enum
from lib import imagecanvas, menu, mapinfo, init_classes, ma_util, top_menu

fpath=os.path.dirname(os.path.realpath(__file__))
photo_dir=os.path.join(fpath,"images")
config_dir=os.path.join(fpath,"config")

scale = 1.0
max_scale = 3.0
min_scale = .10
scale_rate_of_change = 0.25
init_shape_gamedata = None
window_title = "Visual Wld Shape Editor"
no_file_message = "No File Open"

class State(Enum):
  SELECTION = 1
  MOVE = 2
  ROTATE = 3
  
#default to selection mode
state = State.SELECTION
selected_objects = None
dir_name = None

if __name__ == "__main__":
  #forward declarations because hack
  image_canvas = None
  button_menu = None
  def zoom_in():
    global scale
    scale = scale * (1+scale_rate_of_change)
    if scale > max_scale:
      scale = max_scale
    image_canvas.set_scale(scale)

  def zoom_out():
    global scale
    scale = scale * (1-scale_rate_of_change)
    if scale < min_scale:
      scale = min_scale
    image_canvas.set_scale(scale)

  def add_object():
    image_canvas.add_object()

  def add_grid():
    image_canvas.add_grid(100)

  def draw_objects():
    if init_shape_gamedata is not None:
      image_canvas.draw_objects(init_shape_gamedata)
    else :
      print("Open a file first")

  def left_click_callback(event):
    global state
    global selected_objects
    if state == State.SELECTION:
      if init_shape_gamedata is not None:
        shape_list = image_canvas.get_objects_at_pixel(event.x,event.y)
        selected_objects = shape_list
        print("found:", len(shape_list), "objects")
        button_menu.set_selection(shape_list)
        #also display popup if there are selected shapes
        if len(shape_list):
          popup_menu = tkinter.Menu(image_canvas.frame,
                                    tearoff = 0)
  
          popup_menu.add_command(label = "Move",
                                 command = lambda: globals().update(state = State.MOVE))
  
          popup_menu.add_command(label = "Rotate",
                                 command = lambda:globals().update(state = State.ROTATE))
          popup_menu.add_separator()
          popup_menu.add_command(label = "Cancel",
                                    command = lambda:globals().update(state = State.SELECTION))
          try:
            popup_menu.tk_popup(event.x_root, event.y_root)
          finally:
            popup_menu.grab_release()

    elif state == State.MOVE:
      #get selected shape
      value = button_menu.selected_object.get()
      index = button_menu.get_object_index(value)
      init = selected_objects[index][0]
      init.data["Position_X"], init.data["Position_Z"] = image_canvas.pixel_to_wld_coords(event.x, event.y)
      image_canvas.redraw()

      #reset state
      state = State.SELECTION
    elif state == State.ROTATE:
      value = button_menu.selected_object.get()
      index = button_menu.get_object_index(value)
      init = selected_objects[index][0]
      original_x = selected_objects[index][0].data["Position_X"]
      original_z = selected_objects[index][0].data["Position_Z"]
      new_map_x, new_map_z = image_canvas.pixel_to_wld_coords(event.x, event.y)
      #distance formula baby - nulls out rotation
      dist = math.sqrt((original_x - new_map_x)**2 + (original_z - new_map_z)**2)
      init.data["Front_X"] = (new_map_x - original_x)/dist
      init.data["Front_Z"] = (new_map_z - original_z)/dist
      init.data["Front_Y"] = 0
      init.data["Right_X"] = init.data["Front_Z"]
      init.data["Right_Z"] = -init.data["Front_X"]
      init.data["Right_Y"] = 0
      init.data["Up_X"] = 0
      init.data["Up_Y"] = 1
      init.data["Up_Z"] = 0

      image_canvas.redraw()
      #reset state
      state = State.SELECTION
    else:
      print("Unhandled State")


  def dropdown_update(var, idx, mode):
    value = button_menu.selected_object.get()
    index = button_menu.get_object_index(value)
  
  def map_update(var, idx, mode):
    loaded_map = maps[top_menu.get_selected_map()]
    image_canvas.set_new_map(loaded_map, photo_dir)

  def open_wld():
    global init_shape_gamedata
    global dir_name
    dir_name = tkinter.filedialog.askdirectory()
    if dir_name:
      # ma_util.wld_folder_to_init_shape_gamedata returns 4 objects, only care about the last one
      init_shape_gamedata = ma_util.wld_folder_to_init_shape_gamedata(dir_name)[-1]
      tk.title(window_title + " - " + os.path.basename(dir_name))
  
  def save_wld():
    if dir_name is None:
      print("No dir opened")
      return
    if init_shape_gamedata is None:
      print("No Shapes")
      return
    
    for item in init_shape_gamedata:
      init_object_file = open(os.path.join(dir_name, item[3] + "_init_object.json"), "w")
      init_object_file.write(ma_util.pretty_pickle_json(item[0]))
      init_object_file.close()
      if item[1] is not None:
        shape_file = open(os.path.join(dir_name, item[3] + "_shape.json"), "w")
        shape_file.write(ma_util.pretty_pickle_json(item[1]))
        shape_file.close()

      if item[2] is not None:
        gamedata_file = open(os.path.join(dir_name, item[3] + "_gamedata.json"), "w")
        gamedata_file.write(item[2].to_json())
        gamedata_file.close()
  
  #load maps
  maps = []
  for filename in os.listdir(config_dir):
    maps.append(mapinfo.MapInfo(os.path.join(config_dir, filename)))
  loaded_map = maps[0]


  #load shapes
  tk = tkinter.Tk()
  tk.geometry("600x600")
  tk.columnconfigure(0, weight=1)
  tk.rowconfigure(0, weight=1)
  tk.title(window_title + " - " + no_file_message)
  image_canvas = imagecanvas.ImageCanvas(tk, loaded_map, photo_dir, 0,0, left_click_callback)
  top_menu = top_menu.Top_Menu(tk, 1, 0, open_wld, map_update, maps, save_wld)
  button_menu = menu.Menu(tk, 2, 0, zoom_in, zoom_out, add_object, add_grid, draw_objects, dropdown_update)
  tk.mainloop()

