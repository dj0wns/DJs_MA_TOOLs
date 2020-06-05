import os
import tkinter
import tkinter.filedialog
import json
import math
import jsonpickle
from enum import Enum
from threading import Lock
from lib import imagecanvas, menu, mapinfo, init_classes, ma_util, top_menu, edit_pane, add_object_dialog

fpath=os.path.dirname(os.path.realpath(__file__))
photo_dir=os.path.join(fpath,"images")
config_dir=os.path.join(fpath,"config")
template_dir=os.path.join(fpath,"templates")

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

wld_lock = Lock()

if __name__ == "__main__":
  #forward declarations because hack
  tk = tkinter.Tk()
  tk.geometry("1000x600")
  image_canvas = None
  button_menu = None
  right_edit_pane = None
  
  def popup_message(text):
    top = tkinter.Toplevel(tk)
    tkinter.Label(top, text=text).pack()
    tkinter.Button(top, text="Okay", command = top.destroy).pack()
    tk.wait_window(top)


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

  def add_object_response(template_name, shape_name):
    #make sure shape_name is valid
    if "_" in shape_name:
      popup_message("No underscores allows in name")
      return
    if not len(shape_name):
      popup_message("Name must be at least 1 character")
      return
    #check if name is already in use
    for isgn in init_shape_gamedata:
      if isgn[3].lower() == shape_name.lower():
        popup_message("Name is already in use")
        return
    #add template to list of shapes and redraw
    shape = None
    init = None
    gamedata = None
    for file in os.listdir(template_dir):
      if file.startswith(template_name):
        if file.endswith("_init_object.json"):
          print("found init")
          init_object_packed = open(os.path.join(template_dir, file), "rb").read()
          init = jsonpickle.decode(init_object_packed)
        elif file.endswith("_shape.json"):
          print("found shape")
          shape_packed = open(os.path.join(template_dir, file), "rb").read()
          shape = jsonpickle.decode(shape_packed)
        elif file.endswith("_gamedata.json"):
          print("found gamedata")
          gamedata = ma_util.Empty()
          gamedata.__class__ = init_classes.GameDataHeader
          gamedata_json = open(os.path.join(template_dir, file), "r").read()
          gamedata.from_json(gamedata_json)
    #update location 
    x, z = image_canvas.get_visible_center_game_point()
    init.data["Position_X"] = x
    init.data["Position_Z"] = z
    init_shape_gamedata.append([init, shape, gamedata, shape_name])
    image_canvas.redraw()




  def add_object():
    if dir_name is None:
      popup_message("No wld open")
      return
    if init_shape_gamedata is None:
      popup_message("No Shapes")
      return
    #Get template list
    template_list = []
    for file in os.listdir(template_dir):
      if file.endswith("_init_object.json"):
        template_list.append(file[:-17])
        
    d = add_object_dialog.Add_Object_Dialog(tk, template_list, add_object_response)
    tk.wait_window(d.top)

  def add_grid():
    image_canvas.add_grid(100)

  def draw_objects():
    if init_shape_gamedata is not None:
      image_canvas.draw_objects(init_shape_gamedata)
    else :
      popup_message("Open a file first")

  def left_click_callback(event):
    global state
    global selected_objects
    if state == State.SELECTION:
      if init_shape_gamedata is not None:
        shape_list = image_canvas.get_objects_at_pixel(event.x,event.y)
        selected_objects = shape_list
        print("found:", len(shape_list), "objects")
        right_edit_pane.set_selection(shape_list)
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
      value = right_edit_pane.selected_object.get()
      index = right_edit_pane.get_object_index(value)
      init = selected_objects[index][0]
      init.data["Position_X"], init.data["Position_Z"] = image_canvas.pixel_to_wld_coords(event.x, event.y)
      image_canvas.redraw()

      #reset state
      state = State.SELECTION
    elif state == State.ROTATE:
      value = right_edit_pane.selected_object.get()
      index = right_edit_pane.get_object_index(value)
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
    value = right_edit_pane.selected_object.get()
    index = right_edit_pane.get_object_index(value)
    if len(selected_objects):
      right_edit_pane.update_fields(selected_objects[index])
    else:
      right_edit_pane.clear_fields()
      
  
  def save_shape():
    if len(selected_objects):
      print("Saving Shape")
      right_edit_pane.update_shape()
      image_canvas.redraw()
  
  def map_update(var, idx, mode):
    loaded_map = maps[top_menu.get_selected_map()]
    image_canvas.set_new_map(loaded_map, photo_dir)

  def open_wld():
    global init_shape_gamedata
    global dir_name
    with wld_lock:
      dir_name = tkinter.filedialog.askdirectory()
      if dir_name:
        # ma_util.wld_folder_to_init_shape_gamedata returns 4 objects, only care about the last one
        init_shape_gamedata = ma_util.wld_folder_to_init_shape_gamedata(dir_name)[-1]
        tk.title(window_title + " - " + os.path.basename(dir_name))
        draw_objects()
  
  def save_wld():
    global init_shape_gamedata
    with wld_lock:
      if dir_name is None:
        popup_message("No dir opened")
        return
      if init_shape_gamedata is None:
        popup_message("No Shapes")
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
      #lastly reload wld because i cant figure out the duplicate bug
      init_shape_gamedata = ma_util.wld_folder_to_init_shape_gamedata(dir_name)[-1]
      draw_objects()

  
  #load maps
  maps = []
  for filename in os.listdir(config_dir):
    maps.append(mapinfo.MapInfo(os.path.join(config_dir, filename)))
  loaded_map = maps[0]


  tk.grid_columnconfigure(0, weight=1)
  tk.grid_columnconfigure(1, weight=0)
  tk.grid_rowconfigure(0, weight=1)
  tk.title(window_title + " - " + no_file_message)
  left_frame = tkinter.Frame(tk, bd=0, relief=tkinter.SUNKEN)
  left_frame.grid(row=0, column=0, sticky=tkinter.N+tkinter.E+tkinter.W+tkinter.S)
  left_frame.grid_rowconfigure(0, weight=1)
  left_frame.grid_columnconfigure(0, weight=1)
  

  image_canvas = imagecanvas.ImageCanvas(left_frame, loaded_map, photo_dir, 0,0, left_click_callback)
  top_menu = top_menu.Top_Menu(left_frame, 1, 0, open_wld, map_update, maps, save_wld)
  button_menu = menu.Menu(left_frame, 2, 0, zoom_in, zoom_out, add_object, add_grid)
  
  right_edit_pane = edit_pane.Edit_Pane(tk,0,1, dropdown_update, save_shape)
  
  tk.mainloop()

