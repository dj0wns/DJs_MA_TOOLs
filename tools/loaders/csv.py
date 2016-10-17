from loaders.base import Loader


class CSVLoader(Loader):
    def export(self, handle, reader):
        reader.seek(self.entry.location)

        file_length, entry_count, entry_offset, when = reader.read_fmt('IIII')

        reader.seek(self.entry.location + entry_offset)
        entries = [reader.read_fmt('IIHHI') for i in range(entry_count)]

        out_str = ''

        for key_loc, key_len, val_count, idx, val_loc in entries:
            reader.seek(self.entry.location + key_loc)
            key = reader.read_str(key_len)
            out_str += key

            reader.seek(self.entry.location + val_loc)
            for i in range(val_count):
                val_type = reader.read_fmt('I')[0]
                if val_type == 0:  # string
                    str_loc, str_len = reader.read_fmt('II')
                    tmp_pos = reader.pos
                    reader.seek(self.entry.location + str_loc)
                    str_val = reader.read_str(str_len)
                    reader.seek(tmp_pos)
                    out_str += ',"{}"'.format(str_val)
                elif val_type == 1:  # number(float)
                    float_val, _ = reader.read_fmt('fI')
                    out_str += ',{}'.format(float_val)
                elif val_type == 2:  # tuple?
                    tuple_val = reader.read_fmt('II')
                    out_str += ',{}/{}'.format(*tuple_val)
                else:
                    raise Exception('malformed CSV')
            out_str += '\n'

        handle.write(out_str.encode())
