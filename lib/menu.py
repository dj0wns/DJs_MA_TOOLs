import tkinter
import PIL
from PIL import ImageTk


class Menu:
  def __init__(self,root, gridx, gridy, zoom_in, zoom_out, add_object, add_grid, dropdown_update):
    frame = tkinter.Frame(root, bd=2, relief=tkinter.SUNKEN)
    frame.grid(row=gridx, column=gridy, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    add_grid_button = tkinter.Button(frame, text="Add Grid", command=add_grid)
    add_object_button = tkinter.Button(frame, text="Add Object", command=add_object)
    zoom_in_button = tkinter.Button(frame, text="Zoom In", command=zoom_in)
    zoom_out_button = tkinter.Button(frame, text="Zoom Out", command=zoom_out)
    
    self.object_list = ['No Selection']
    self.selected_object = tkinter.StringVar(frame)
    self.selected_object.set('No Selection')
    self.selected_object_menu = tkinter.OptionMenu(frame, self.selected_object, *self.object_list)

    
    self.selected_object.trace('w', dropdown_update)

    add_object_button.grid(row=0, column=0)
    add_grid_button.grid(row=0, column=1)
    zoom_in_button.grid(row=0, column=2)
    zoom_out_button.grid(row=0, column=3)
    self.selected_object_menu.grid(row=0, column=6)

  def get_object_index(self, selection):
    if selection in self.object_list:
      return self.object_list.index(selection)
    else: 
      return -1
    

  def set_selection(self, shape_list):
    self.selected_object_menu['menu'].delete(0, 'end')
    self.object_list = []
    if len(shape_list):
      
      # Reset var and delete all old options
      self.selected_object_menu['menu'].delete(0, 'end')

      # Insert list of new options (tk._setit hooks them up to var)
      for shape in shape_list:
        name = shape[3]
        self.object_list.append(name)
        self.selected_object_menu['menu'].add_command(label=name, command=tkinter._setit(self.selected_object, name))

      self.selected_object.set(shape_list[0][3])
    else:
      # Reset var and delete all old options
      self.selected_object.set("No Selection")
