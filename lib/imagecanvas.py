import tkinter
import os
import PIL
import math
from PIL import ImageTk, ImageDraw
from . import mapinfo


class ImageCanvas:
  def __init__(self, root, map_info, photo_dir, gridx, gridy, left_click_callback):
    self.scale = 1.0
    self.max_scale = 1.7
    self.min_scale = 0.25
    self.rect_size = 4
    self.img_id = None
    self.grid_id = None
    self.obj_id = None
    self.map_info = map_info
    frame = tkinter.Frame(root, bd=2, relief=tkinter.SUNKEN)
    frame.grid(row=gridx, column=gridy, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    xscrollbar = tkinter.Scrollbar(frame, orient=tkinter.HORIZONTAL)
    yscrollbar = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL)

    xscrollbar.grid(row=1, column=0, sticky=tkinter.E+tkinter.W)
    yscrollbar.grid(row=0, column=1, sticky=tkinter.N+tkinter.S)
    
    self.canvas = tkinter.Canvas(frame, bd=5, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, \
                                 xscrollincrement = 10, yscrollincrement = 10)
    self.canvas.grid(row=0, column=0, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)
   
    self.orig_img = PIL.Image.open(os.path.join(photo_dir, map_info.data["file_name"]))

    self.img = PIL.ImageTk.PhotoImage(self.orig_img)
    #self.add_grid(25)
    self.redraw()
    xscrollbar.config(command=self.canvas.xview)
    yscrollbar.config(command=self.canvas.yview)
    
    #frame.pack(fill="both", expand=True)

    self.canvas.bind("<Button 1>", left_click_callback)
    self.canvas.bind("<Button 3>", self.grab)
    self.canvas.bind("<B3-Motion>", self.drag)

  def get_objects_at_pixel(self,x,y):
    canvas_x = self.canvas.canvasx(x)
    canvas_y = self.canvas.canvasy(y)
    image_x = canvas_x/self.scale + self.map_info.data['x_dimension']/2
    image_y = canvas_y/self.scale + self.map_info.data['y_dimension']/2
    print(image_x, image_y)
    retlist = []
    for item in self.init_shape_gamedata:
      map_x = item[0].data['Position_X']
      map_z = item[0].data['Position_Z']
      d_pixel_x = map_x * self.map_info.data["image_pixels_per_map_x"][0] + map_z * self.map_info.data["image_pixels_per_map_z"][0]  
      d_pixel_y = map_x * self.map_info.data["image_pixels_per_map_x"][1] + map_z * self.map_info.data["image_pixels_per_map_z"][1]  
      pixel_x = d_pixel_x + self.map_info.data['x_center']
      pixel_y = d_pixel_y + self.map_info.data['y_center']
      #set scale
      pixel_x = pixel_x
      pixel_y = pixel_y
      
      border = self.rect_size / self.scale

      if abs(pixel_x - image_x) <= border and abs(pixel_y - image_y) <= border:
        retlist.append(item)
    return retlist

    

  def grab(self, event):
    self._x = event.x
    self._y = event.y
    canvas_x = self.canvas.canvasx(event.x)
    canvas_y = self.canvas.canvasy(event.y)
    image_x = canvas_x/self.scale + self.map_info.data['x_dimension']/2
    image_y = canvas_y/self.scale + self.map_info.data['y_dimension']/2
    d_x = image_x - self.map_info.data['x_center']
    d_y = image_y - self.map_info.data['y_center']
    map_x = d_x * self.map_info.data["map_per_pixel_x"][0] + d_y * self.map_info.data["map_per_pixel_y"][0]
    map_y = d_x * self.map_info.data["map_per_pixel_x"][1] + d_y * self.map_info.data["map_per_pixel_y"][1]
    print("Canvas Coordinates")
    print (canvas_x, canvas_y)
    print("image Coordinates")
    print (image_x, image_y)
    print("Distance from map 0,0 in pixels")
    print (d_x, d_y)
    print("Estimated map coords")
    print (map_x, map_y)


  def drag (self, event): 
    if (self._x-event.x < 0):
      self.canvas.xview("scroll",-1,"units")
    elif (self._x-event.x > 0):
      self.canvas.xview("scroll",1,"units")
    if (self._y-event.y < 0):
      self.canvas.yview("scroll",-1,"units")
    elif (self._y-event.y > 0):
      self.canvas.yview("scroll",1,"units")
    self._x = event.x
    self._y = event.y

  def add_grid(self, line_spacing):
    self.grid_size = line_spacing
    self.grid_id = True
    line_spacing = line_spacing * self.scale
    x_dim = int(self.map_info.data['x_dimension'] * self.scale)
    y_dim = int(self.map_info.data['y_dimension'] * self.scale)
    pixels_per_x = self.map_info.data["image_pixels_per_map_x"]
    pixels_per_z = self.map_info.data["image_pixels_per_map_z"]
    
    self.grid_orig = PIL.Image.new('RGBA', (x_dim, y_dim), (255, 0, 0, 0))
    self.draw = PIL.ImageDraw.Draw(self.grid_orig)
    
    line_width= 2

    #draw origin line
    center_x = self.map_info.data['x_center'] * self.scale
    center_y = self.map_info.data['y_center'] * self.scale
    #find the x axis
    #y = mx + b you know the drill
    m = (pixels_per_x[1]/pixels_per_x[0])
    b = center_y - center_x * m
    #now find the 2 edge intersects (y = 0, y = max) and then make it relative to center
    x_0 = (0 - b) / m
    x_1 = (y_dim - b) / m
    x_axis = ((x_0,0), (x_1, y_dim))
    self.draw.line(x_axis, fill=(255,128,255,255), width=line_width)

    #add more positive x_axis lines
    new_x = center_x
    new_y = center_y
    while new_x < x_dim and new_y < y_dim \
        and new_x > 0 and new_y > 0:
      new_x = new_x + line_spacing * pixels_per_z[0]
      new_y = new_y + line_spacing * pixels_per_z[1]
      b = new_y - new_x * m
      x_0 = (0 - b) / m
      x_1 = (y_dim - b) / m
      line = ((x_0,0), (x_1, y_dim))
      self.draw.line(line, fill=(255,255,255,255), width=line_width)
    
    #add more negative x_axis lines
    new_x = center_x
    new_y = center_y
    while new_x < x_dim and new_y < y_dim \
        and new_x > 0 and new_y > 0:
      new_x = new_x - line_spacing * pixels_per_z[0]
      new_y = new_y - line_spacing * pixels_per_z[1]
      b = new_y - new_x * m
      x_0 = (0 - b) / m
      x_1 = (y_dim - b) / m
      line = ((x_0,0), (x_1, y_dim))
      self.draw.line(line, fill=(255,255,255,255), width=line_width)

    
    #find the z axis
    m = (pixels_per_z[1]/pixels_per_z[0])
    b = center_y - center_x * m
    #now fine the 2 edge intersects (y = 0, y = max)
    y_0 = m*0 + b
    y_1 = m*x_dim + b

    y_axis = ((0,y_0), (x_dim, y_1))
    self.draw.line(y_axis, fill=(255,128,255,255), width=line_width)
    
    #add more positive z_axis lines
    new_x = center_x
    new_y = center_y
    while new_x < x_dim and new_y < y_dim \
        and new_x > 0 and new_y > 0:
      new_x = new_x + line_spacing * pixels_per_x[0]
      new_y = new_y + line_spacing * pixels_per_x[1]
      b = new_y - new_x * m
      y_0 = m*0 + b
      y_1 = m*x_dim + b
      line = ((0,y_0), (x_dim, y_1))
      self.draw.line(line, fill=(255,255,255,255), width=line_width)
    
    #add more negative z_axis lines
    new_x = center_x
    new_y = center_y
    while new_x < x_dim and new_y < y_dim \
        and new_x > 0 and new_y > 0:
      new_x = new_x - line_spacing * pixels_per_x[0]
      new_y = new_y - line_spacing * pixels_per_x[1]
      b = new_y - new_x * m
      y_0 = m*0 + b
      y_1 = m*x_dim + b
      line = ((0,y_0), (x_dim, y_1))
      self.draw.line(line, fill=(255,255,255,255), width=line_width)
    
    self.grid_img = PIL.ImageTk.PhotoImage(self.grid_orig)
    self.grid_id = self.canvas.create_image(0, 0, image=self.grid_img)

    

  def set_scale(self,scale):
    if self.scale == scale:
      #nothing to do here
      return 
    self.scale = scale
    self.redraw(0, 0)
  
  def add_object(self):
    print("add object")
  
  def draw_objects(self, init_shape_gamedata):
    self.init_shape_gamedata = init_shape_gamedata
    line_len = 10
    x_dim = int(self.map_info.data['x_dimension'] * self.scale)
    y_dim = int(self.map_info.data['y_dimension'] * self.scale)
    self.obj_orig = PIL.Image.new('RGBA', (x_dim, y_dim), (255, 0, 0, 0))
    self.obj_draw = PIL.ImageDraw.Draw(self.obj_orig)

    for item in self.init_shape_gamedata:
      map_x = item[0].data['Position_X']
      map_z = item[0].data['Position_Z']
      d_pixel_x = map_x * self.map_info.data["image_pixels_per_map_x"][0] + map_z * self.map_info.data["image_pixels_per_map_z"][0]  
      d_pixel_y = map_x * self.map_info.data["image_pixels_per_map_x"][1] + map_z * self.map_info.data["image_pixels_per_map_z"][1]  
      pixel_x = d_pixel_x + self.map_info.data['x_center']
      pixel_y = d_pixel_y + self.map_info.data['y_center']
      #set scale
      pixel_x = pixel_x * self.scale
      pixel_y = pixel_y * self.scale
      #switch color on type
      #Default white
      color = (255,255,255,255)
      if item[2] is not None:
        for table in item[2].tables:
          keystring = table.data['keystring'].decode()
          if keystring.lower() == "type":
            if "bot" in table.fields[0].data_string().lower():
              #blue
              color = (0,0,255,255)
            elif  "siteweapon" in table.fields[0].data_string().lower():
              #lightblue
              color = (135,206,250,255)
            elif  "console" in table.fields[0].data_string().lower():
              #yellow
              color = (255,255,102,255)
            elif  "goodie" in table.fields[0].data_string().lower():
              #green
              color = (124,252,0,255)
      self.obj_draw.rectangle([(pixel_x - self.rect_size, pixel_y - self.rect_size),(pixel_x + self.rect_size, pixel_y + self.rect_size)],  fill=color)
      #add little direction arrow - lets assume the objects are flat because fuck it - only draw front
      f_x = item[0].data['Front_X']
      f_y = item[0].data['Front_Y']
      f_z = item[0].data['Front_Z']
      #these numbers are relative to the map coords to have to convert them to pixels
      f_pixel_x = f_x * self.map_info.data["image_pixels_per_map_x"][0] + f_z * self.map_info.data["image_pixels_per_map_z"][0]
      f_pixel_y = f_x * self.map_info.data["image_pixels_per_map_x"][1] + f_z * self.map_info.data["image_pixels_per_map_z"][1]

      f_pixel_magnitude = math.sqrt(f_pixel_x * f_pixel_x + f_pixel_y * f_pixel_y)
      #set to unit vector and multiply by length
      # And avoid pesky divide by 0 errors if the front is vertical for some stupid reason
      if f_pixel_magnitude != 0:
        f_pixel_x = f_pixel_x / f_pixel_magnitude * line_len
        f_pixel_y = f_pixel_y / f_pixel_magnitude * line_len
      else:
        f_pixel_x =  0
        f_pixel_y =  0
      line = ((pixel_x,pixel_y),(pixel_x + f_pixel_x, pixel_y + f_pixel_y))
      self.obj_draw.line(line, fill=color, width=1)
    self.obj_img = PIL.ImageTk.PhotoImage(self.obj_orig)
    self.obj_id = self.canvas.create_image(0, 0, image=self.obj_img)

  def redraw(self, x=0, y=0):
    if self.img_id:
        self.canvas.delete(self.img_id)
    iw, ih = self.orig_img.size
    size = int(iw * self.scale), int(ih * self.scale)
    self.img = PIL.ImageTk.PhotoImage(self.orig_img.resize(size))
    self.img_id = self.canvas.create_image(x, y, image=self.img)
    if self.grid_id:
      self.add_grid(self.grid_size)
    if self.obj_id:
      self.draw_objects(self.init_shape_gamedata)

    # tell the canvas to scale up/down the vector objects as well
    self.canvas.scale(tkinter.ALL, x, y, self.scale, self.scale)
    self.canvas.config(scrollregion=self.canvas.bbox(tkinter.ALL))

    
