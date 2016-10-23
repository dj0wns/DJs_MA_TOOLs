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
    def export(self, handle, reader):
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
                    values.append('a:' + str_val)
                elif val_type == 1:  # number(float)
                    float_val, _ = reader.read_fmt('fI')
                    values.append(float_val)
                elif val_type == 2:  # utf16 string
                    str_loc, str_len = reader.read_fmt('II')
                    tmp_pos = reader.pos
                    reader.seek(self.entry.location + str_loc)
                    str_val = reader.handle.read(str_len * 2).decode('utf-16-le')
                    reader.seek(tmp_pos)
                    values.append('u:' + str_val)
                else:
                    raise Exception('malformed CSV')

            out_dict[key] = values

        handle.write(json.dumps(out_dict).encode())
