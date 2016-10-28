import struct

from loaders.base import Loader


class TGALoader(Loader):
    def read(self, reader):
        reader.seek(self.entry.location)
        self.data = {}

        name = reader.handle.read(20)
        name = name[:name.index(0)].decode()
        flags, unk_null, width, height = reader.read_fmt("IIHH")
        self.data['header'] = {
            'name': name,
            'flags': flags,
            'width': width,
            'height': height,
        }
        unk_nulls = reader.read_fmt('I' * 24)
        self.data['texture'] = reader.handle.read(self.entry.length - 128)
        # print('{0:32b}'.format(self.data['header']['flags']))

    def write(self, writer):
        pass

    def save(self, handle):
        # this is a disgrace, TODO: don't completely yolo the DDS header

        hdr = self.data['header']
        tex = self.data['texture']

        handle.write(b'DDS ')
        handle.write(struct.pack(
            20 * 'I',
            124,
            hdr['flags'],  # 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000,
            hdr['height'],
            hdr['width'],
            hdr['height'] * hdr['width'],
            0,
            0,  # mipmapcount, 8?
            0,
            *([0] * 10),
            32,
            4
        ))
        handle.write(b'DXT3')
        handle.write(struct.pack(
            10 * 'I',
            *([0] * 5),
            4198408,
            *([0] * 4),
        ))
        handle.write(tex)

    def load(self, handle):
        pass
