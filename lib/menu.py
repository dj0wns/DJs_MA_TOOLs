import tkinter
import PIL
from PIL import ImageTk


class Menu:
  def __init__(self,root, gridx, gridy, zoom_in, zoom_out, add_object, add_grid, draw_objects):
    frame = tkinter.Frame(root, bd=2, relief=tkinter.SUNKEN)
    frame.grid(row=gridx, column=gridy, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    add_grid_button = tkinter.Button(frame, text="Add Grid", command=add_grid)
    add_object_button = tkinter.Button(frame, text="Add Object", command=add_object)
    zoom_in_button = tkinter.Button(frame, text="Zoom In", command=zoom_in)
    zoom_out_button = tkinter.Button(frame, text="Zoom Out", command=zoom_out)
    draw_objects_button = tkinter.Button(frame, text="Draw Objects", command=draw_objects)

    
    add_object_button.grid(row=0, column=0)
    add_grid_button.grid(row=0, column=1)
    zoom_in_button.grid(row=0, column=2)
    zoom_out_button.grid(row=0, column=3)
    draw_objects_button.grid(row=0, column=4)
