import json

from loaders.base import Loader

"""
Dump everything in the format:

type 0 ascii str - "a:string"
type 1 float num - 123
type 2 utf16 str - "u:string"

ex:
{
    "some_key": ["u:äöõö", 123, "a:hello", ...],
    "some_other_key": [956, "a:halo", ...],
    ...
}
"""


class CSVLoader(Loader):
    def read(self, reader):
        reader.seek(self.entry.location)

        file_length, entry_count, entry_offset, when = reader.read_fmt('IIII')

        reader.seek(self.entry.location + entry_offset)
        entries = [reader.read_fmt('IIHHI') for i in range(entry_count)]

        out_dict = {}

        for key_loc, key_len, val_count, idx, val_loc in entries:
            reader.seek(self.entry.location + key_loc)
            key = reader.read_str(key_len)

            values = []

            reader.seek(self.entry.location + val_loc)
            for i in range(val_count):
                val_type = reader.read_fmt('I')[0]

                if val_type == 0:  # string
                    str_loc, str_len = reader.read_fmt('II')
                    tmp_pos = reader.pos
                    reader.seek(self.entry.location + str_loc)
                    str_val = reader.read_str(str_len)
                    reader.seek(tmp_pos)
                    values.append(str_val)
                elif val_type == 1:  # number(float)
                    float_val, _ = reader.read_fmt('fI')
                    if float_val >= 1 or float_val == 0:
                      values.append(int(float_val))
                    else:
                      values.append(float("{0:.1f}".format(float_val)))
                elif val_type == 2:  # utf16 string
                    str_loc, str_len = reader.read_fmt('II')
                    tmp_pos = reader.pos
                    reader.seek(self.entry.location + str_loc)
                    if reader.little_endian:
                      str_val = reader.handle.read(str_len * 2).decode('utf-16le')
                    else:
                      str_val = reader.handle.read(str_len * 2).decode('utf-16be')

                    reader.seek(tmp_pos)
                    values.append(str_val)
                else:
                    raise Exception('malformed CSV')

            out_dict[key] = values

        self.data = out_dict

    def save(self, handle):
        for key in self.data.keys():
          handle.write(key.encode('ascii', 'ignore'))
          handle.write(",".encode())
          for item in self.data[key]:
            if isinstance(item, str):
              handle.write(item.encode('ascii', "ignore"))
              handle.write(",".encode())
            else:
              handle.write(str(item).encode('ascii', 'ignore'))
              handle.write(",".encode())
          handle.write("\n".encode())



    def reimport(self, handle):
        self.data = json.loads(handle.read().decode())
