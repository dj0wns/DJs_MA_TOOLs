import tkinter
import PIL
from PIL import ImageTk


class Top_Menu:
  def __init__(self,root, gridx, gridy, open_wld, map_update, map_list, save_wld,
               zoom_in, zoom_out, add_object, toggle_grid):
    frame = tkinter.Frame(root, bd=2, relief=tkinter.SUNKEN)
    frame.grid(row=gridx, column=gridy, sticky=tkinter.N+tkinter.E+tkinter.W)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_columnconfigure(0, weight=0)
    
    open_wld_button = tkinter.Button(frame, text="Open Wld Folder", command=open_wld)
    save_wld_button = tkinter.Button(frame, text="Save Wld", command=save_wld)
    
    self.map_names = [ m.data['file_name'] for m in map_list ]
    self.selected_map = tkinter.StringVar(frame)
    self.selected_map.set(self.map_names[0])
    self.selected_map_menu = tkinter.OptionMenu(frame, self.selected_map, *self.map_names)


    
    self.selected_map.trace('w', map_update)

    toggle_grid_button = tkinter.Button(frame, text="Toggle Grid", command=toggle_grid)
    add_object_button = tkinter.Button(frame, text="Add Object", command=add_object)
    zoom_in_button = tkinter.Button(frame, text="Zoom In", command=zoom_in)
    zoom_out_button = tkinter.Button(frame, text="Zoom Out", command=zoom_out)
    
    open_wld_button.grid(row=0, column=0)
    self.selected_map_menu.grid(row=0, column=1)
    save_wld_button.grid(row=0, column=2)
    add_object_button.grid(row=0, column=3)
    toggle_grid_button.grid(row=0, column=4)
    zoom_in_button.grid(row=0, column=5)
    zoom_out_button.grid(row=0, column=6)

  def get_selected_map(self):
    if self.selected_map.get() in self.map_names:
      return self.map_names.index(self.selected_map.get())
    else: 
      return -1
