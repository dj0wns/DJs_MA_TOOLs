import os
import tkinter
import json
from lib import imagecanvas, menu, mapinfo, init_classes, ma_util

fpath=os.path.dirname(os.path.realpath(__file__))
photo_dir=os.path.join(fpath,"images")
config_dir=os.path.join(fpath,"config")

scale = 1.0
max_scale = 3.0
min_scale = .10
scale_rate_of_change = 0.25

loaded_map = mapinfo.MapInfo(os.path.join(config_dir,"wemccity_02.json"))


if __name__ == "__main__":
  #forward declarations because hack
  image_canvas = None
  button_menu = None
  init_shape_gamedata = None
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
    image_canvas.draw_objects(init_shape_gamedata)

  def left_click_callback(event):
    print ("left click", event.x, event.y)
    shape_list = image_canvas.get_objects_at_pixel(event.x,event.y)
    print("found:", len(shape_list), "objects")
    #button_menu.set_selection("item name")

  #load shapes
  init_shape_gamedata =  ma_util.wld_folder_to_init_shape_gamedata("./wemccity_02")[-1]
  tk = tkinter.Tk()
  tk.geometry("600x600")
  tk.columnconfigure(0, weight=1)
  tk.rowconfigure(0, weight=1)
  image_canvas = imagecanvas.ImageCanvas(tk, loaded_map, photo_dir, 0,0, left_click_callback)
  button_menu = menu.Menu(tk, 1, 0, zoom_in, zoom_out, add_object, add_grid, draw_objects)
  tk.mainloop()

