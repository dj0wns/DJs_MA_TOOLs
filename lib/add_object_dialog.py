import tkinter
import PIL
from PIL import ImageTk


class Add_Object_Dialog:
  def __init__(self, root, dropdown_list, callback):
    self.top = tkinter.Toplevel(root)
    self.callback = callback

    tkinter.Label(self.top, text="Template").pack()

    self.object_list = dropdown_list
    self.selected_object = tkinter.StringVar(self.top)
    self.selected_object.set(dropdown_list[0])
    self.selected_object_menu = tkinter.OptionMenu(self.top, self.selected_object, *self.object_list)
    self.selected_object_menu.pack()

    tkinter.Label(self.top, text="Name").pack()
    self.name = tkinter.Entry(self.top)
    self.name.pack(padx=5)

    button_bar = tkinter.Frame(self.top)

    ok_button = tkinter.Button(button_bar, text="Ok", command=self.ok)
    ok_button.pack(side=tkinter.LEFT)
    
    cancel_button = tkinter.Button(button_bar, text="Cancel", command=self.cancel)
    cancel_button.pack(side=tkinter.LEFT)

    button_bar.pack()

  def ok(self):
    shape_name = self.name.get()
    selected_object_name = self.selected_object.get()

    self.top.destroy()
    self.callback(selected_object_name, shape_name)
  
  def cancel(self):
    self.top.destroy()
