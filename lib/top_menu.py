import tkinter
import PIL
from PIL import ImageTk


class Top_Menu:
  def __init__(self,root, gridx, gridy, open_wld, map_update, map_list, save_wld):
    frame = tkinter.Frame(root, bd=2, relief=tkinter.SUNKEN)
    frame.grid(row=gridx, column=gridy, sticky=tkinter.N+tkinter.E+tkinter.W)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_columnconfigure(0, weight=0)
    
    open_wld_button = tkinter.Button(frame, text="Open Extracted Wld", command=open_wld)
    save_wld_button = tkinter.Button(frame, text="Save Extracted Wld", command=save_wld)
    
    self.map_names = [ m.data['file_name'] for m in map_list ]
    self.selected_map = tkinter.StringVar(frame)
    self.selected_map.set(self.map_names[0])
    self.selected_map_menu = tkinter.OptionMenu(frame, self.selected_map, *self.map_names)


    
    self.selected_map.trace('w', map_update)

    open_wld_button.grid(row=0, column=0)
    self.selected_map_menu.grid(row=0, column=1)
    save_wld_button.grid(row=0, column=2)

  def get_selected_map(self):
    if self.selected_map.get() in self.map_names:
      return self.map_names.index(self.selected_map.get())
    else: 
      return -1
