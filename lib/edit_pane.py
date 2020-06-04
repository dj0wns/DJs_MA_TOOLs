import tkinter
import PIL
from PIL import ImageTk
from . import init_classes, ma_util


class Edit_Pane:
  def __init__(self,root, gridx, gridy, dropdown_update, save_shape):
    self.entry_fields_dict = {}
    self.gamedata_dict = []
    self.field_frame = None
    self.frame = tkinter.Frame(root, bd=0, relief=tkinter.SUNKEN)
    self.frame.grid(row=gridx, column=gridy, sticky=tkinter.N+tkinter.E+tkinter.W)
    self.frame.grid_rowconfigure(0, weight=0)
    self.frame.grid_columnconfigure(0, weight=1)
    
    self.object_list = ['No Selection']
    self.selected_object = tkinter.StringVar(self.frame)
    self.selected_object.set('No Selection')
    self.selected_object_menu = tkinter.OptionMenu(self.frame, self.selected_object, *self.object_list)
    
    self.selected_object.trace('w', dropdown_update)

    self.selected_object_menu.config(width=15)
    self.selected_object_menu.grid(row=0, column=0)

    save_shape_button = tkinter.Button(self.frame, text="Save Shape", command=save_shape)
    save_shape_button.grid(row=3, column=0)

  #updates local shape with the values in the text boxes
  def update_shape(self):
    if self.entry_fields_dict is None:
      return
    if self.shape is None:
      return
    for key, value in self.entry_fields_dict.items():
      #sadly have to hardcode, no way around it
      if key == "Pos_X":
        self.shape[0].data['Position_X'] = float(float(value.get()))
      elif key == "Pos_Y":
        self.shape[0].data['Position_Y'] = float(value.get())
      elif key == "Pos_Z":
        self.shape[0].data['Position_Z'] = float(value.get())
      elif key == "Front_X":
        self.shape[0].data['Front_X'] = float(value.get())
      elif key == "Front_Y":
        self.shape[0].data['Front_Y'] = float(value.get())
      elif key == "Front_Z":
        self.shape[0].data['Front_Z'] = float(value.get())
      elif key == "Right_X":
        self.shape[0].data['Right_X'] = float(value.get())
      elif key == "Right_Y":
        self.shape[0].data['Right_Y'] = float(value.get())
      elif key == "Right_Z":
        self.shape[0].data['Right_Z'] = float(value.get())
      elif key == "Up_X":
        self.shape[0].data['Up_X'] = float(value.get())
      elif key == "Up_Y":
        self.shape[0].data['Up_Y'] = float(value.get())
      elif key == "Up_Z":
        self.shape[0].data['Up_Z'] = float(value.get())
      elif key == "Mesh Name":
        self.shape[1].data['mesh'].mesh_name = value.get()
    if self.gamedata_list is not None:
      #Recreate gamedata from scratch
      new_gamedata = ma_util.default_gamedata()
      for row in self.gamedata_list:
        elem = 0
        key = ""
        fields = []
        types = []
        for value in row:
          if elem == 0:
            #key element
            key = value.get()
          elif value.get() != "":
            fields.append(value.get())
            try:
              f_value = float(value.get())
              types.append("FLOAT")
            except:
              types.append("STRING")
          elem += 1
        if key != "":
          ma_util.add_table_to_gamedata(new_gamedata, key, fields, types)
      #now overwrite
      self.shape[2] = new_gamedata
    #now update fields to keep everything recent and relevant
    self.update_fields(self.shape)

      

  def clear_fields(self):
    self.entry_fields_dict = {}
    self.gamedata_list = []
    if self.field_frame is not None:
      self.field_frame.destroy()
      

  def update_fields(self, shape):
    #clear to prevent orphan fields
    self.clear_fields()
    #only canvas can have scroll bars so place frame in canvas
    canvas = tkinter.Canvas(self.frame)
    canvas.grid(row=1, column=0, sticky=tkinter.N+tkinter.E+tkinter.W+tkinter.S)
    canvas.grid_columnconfigure(0, weight=1)
    canvas.grid_rowconfigure(0, weight=1)
    scrollbar = tkinter.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=1, column=1, sticky=tkinter.N+tkinter.S+tkinter.E)
    scrollbar.grid_columnconfigure(0, weight=1)
    scrollbar.grid_rowconfigure(0, weight=1)

    self.field_frame = tkinter.Frame(canvas, bd=2, relief=tkinter.SUNKEN)
    self.field_frame.grid(row=1, column=0, sticky=tkinter.N+tkinter.E+tkinter.W+tkinter.S)
    self.field_frame.grid_rowconfigure(0, weight=1)
    self.field_frame.grid_columnconfigure(0, weight=1)
    
    self.field_frame.bind(
      "<Configure>",
      lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
      )
    )
    canvas.create_window((0, 0), window=self.field_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    self.shape = shape
    row=1
    #Position
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Pos_X", shape[0].data['Position_X']))
    row+=1
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Pos_Y", shape[0].data['Position_Y']))
    row+=1
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Pos_Z", shape[0].data['Position_Z']))
    
    row+=1
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Front_X", shape[0].data['Front_X']))
    row+=1
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Front_Y", shape[0].data['Front_Y']))
    row+=1
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Front_Z", shape[0].data['Front_Z']))

    row+=1
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Right_X", shape[0].data['Right_X']))
    row+=1
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Right_Y", shape[0].data['Right_Y']))
    row+=1
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Right_Z", shape[0].data['Right_Z']))
    
    row+=1
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Up_X", shape[0].data['Up_X']))
    row+=1
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Up_Y", shape[0].data['Up_Y']))
    row+=1
    self.entry_fields_dict.update(
        self.add_text_entry_field(self.field_frame, row, "Up_Z", shape[0].data['Up_Z']))
    
    row+=1
    self.add_labeled_text(self.field_frame, row, "Shape_Type: ",
        init_classes.human_readable_shape_value[shape[0].data['shape_type']])
    
    if shape[0].data['shape_type'] == "FWORLD_SHAPETYPE_MESH":
      row+=1
      self.entry_fields_dict.update(
          self.add_text_entry_field(self.field_frame, row, "Mesh Name", shape[1].data['mesh'].mesh_name))

    if shape[2] is not None:
      table_index = 0
      for table in shape[2].tables:
        field_index = 0
        values = []
        row+=1
        ret_dict = self.add_text_entry_field(self.field_frame, row, "Table "  + str(table_index),
            table.data['keystring'])
        values.append(list(ret_dict.values())[0])
        for field in table.fields:
          row+=1
          ret_dict = self.add_indented_text_entry_field(self.field_frame, row, 1, "Field "  + str(field_index),
              field.data_string())
          values.append(list(ret_dict.values())[0])
          field_index += 1
        #add new field buttons
        row+=1
        command = lambda i=table_index : self.add_data_field(i)
        self.add_indented_button(self.field_frame, row, 1, "Add Field", command)

        self.gamedata_list.append(values)
        table_index += 1
      
      row+=1
      command = lambda : self.add_data_table()
      self.add_indented_button(self.field_frame, row, 1, "Add Table", command)
  
  def add_data_table(self):
    ret_dict = self.add_text_entry_field(self.field_frame, 0, "New Table" , "New Table")
    self.gamedata_list.append([list(ret_dict.values())[0]])
    self.update_shape()

  def add_data_field(self, table_index):
    ret_dict = self.add_indented_text_entry_field(self.field_frame, 0, 1, "New Field" , "New Field")
    self.gamedata_list[table_index].append(list(ret_dict.values())[0])
    self.update_shape()
    

  def add_indented_button(self, root, row, indent, title, command):
    indent_size = 16
    total_indent = indent_size * indent
    frame = tkinter.Frame(root, bd=0, relief=tkinter.SUNKEN, padx=total_indent)
    frame.grid(row=row, column=0, sticky=tkinter.N+tkinter.E+tkinter.W)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_columnconfigure(0, weight=0)
    
    button =  tkinter.Button(frame, text=title, command=command)
    button.grid(row=0, column=0)
    return button
      
  def add_indented_text_entry_field(self, root, row, indent, title, value):
    indent_size = 16
    total_indent = indent_size * indent
    frame = tkinter.Frame(root, bd=0, relief=tkinter.SUNKEN, padx=total_indent)
    frame.grid(row=row, column=0, sticky=tkinter.N+tkinter.E+tkinter.W)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_columnconfigure(0, weight=0)

    label = tkinter.Label(frame, text=title).grid(row=0, column=0)
    entry = tkinter.Entry(frame)
    entry.insert(tkinter.END, value)
    entry.grid(row=0, column=1)
    return {title : entry}

  def add_text_entry_field(self, root, row, title, value):
    frame = tkinter.Frame(root, bd=0, relief=tkinter.SUNKEN)
    frame.grid(row=row, column=0, sticky=tkinter.N+tkinter.E+tkinter.W)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_columnconfigure(0, weight=0)

    label = tkinter.Label(frame, text=title).grid(row=0, column=0)
    entry = tkinter.Entry(frame)
    entry.insert(tkinter.END, value)
    entry.grid(row=0, column=1)
    return {title : entry}
  
  def add_labeled_text(self, root, row, title, value):
    frame = tkinter.Frame(root, bd=0, relief=tkinter.SUNKEN)
    frame.grid(row=row, column=0, sticky=tkinter.N+tkinter.E+tkinter.W)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_columnconfigure(0, weight=0)

    label = tkinter.Label(frame, text=title).grid(row=0, column=0)
    value = tkinter.Label(frame, text=value).grid(row=0, column=1)

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
