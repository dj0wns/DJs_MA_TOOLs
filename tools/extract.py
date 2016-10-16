import argparse
import datetime
import os
import struct
from enum import Enum


class BinaryIO:
    def __init__(self, fh):
        self.handle = fh
        self.endian_prefix = '<'

    @property
    def little_endian(self):
        return self.endian_prefix == '<'

    @little_endian.setter
    def little_endian(self, is_little):
        self.endian_prefix = '<' if is_little else '>'

    def read_fmt(self, fmt, length=None):
        real_fmt = self.endian_prefix + fmt
        buf = self.handle.read(length or struct.calcsize(real_fmt))
        return struct.unpack(real_fmt, buf)

    def read_str(self, length):
        return self.handle.read(length).decode()

    def seek(self, location):
        self.handle.seek(location)  # from start by default


class ProtocolException(Exception):
    pass


class GamePlatform(Enum):
    xbox = 0
    playstation = 1
    gamecube = 2


class MST:
    def __init__(self):
        self.platform = None
        self.package_size = 0
        self.file_count = 0
        self.prefix_unknown = 0
        self.suffix_unknowns = []
        self.files = []

    def read(self, reader: BinaryIO):
        header = reader.read_str(4)  # FANG
        if header == 'FANG':  # Xbox, PS2
            reader.little_endian = True
        elif header == 'GNAF':
            reader.little_endian = False
            reader.platform = GamePlatform.gamecube
        else:
            raise ProtocolException()

        unknown, self.package_size, self.file_count = reader.read_fmt('III')
        suffix_unknowns = reader.read_fmt('I' * 23)

        if reader.little_endian:
            # no idea what this is, but seems to be 3 in PS2 builds, 2 in Xbox & GC
            platform_id = suffix_unknowns[14]
            if platform_id == 3:
                self.platform = GamePlatform.playstation
            elif platform_id == 2:
                self.platform = GamePlatform.xbox
            else:
                raise ProtocolException()

        self.files = []
        for i in range(self.file_count):
            file = MSTFile()
            file.read(reader, self.platform)
            self.files.append(file)


class MSTFile:
    def __init__(self):
        self.name = None
        self.location = 0
        self.length = 0
        self.create_date = None
        self.unknown = 0

    def read(self, reader: BinaryIO, platform: GamePlatform):
        name_length = 24 if platform == GamePlatform.playstation else 20
        self.name = reader.read_str(name_length).split('\0')[0]  # important to re-add this when writing
        self.location, self.length, timestamp, self.unknown = reader.read_fmt('IIII')
        self.create_date = datetime.date.fromtimestamp(timestamp)

    def dump_contents(self, handle, reader: BinaryIO):
        reader.seek(self.location)
        # kind of like shutil.copyfileobj, but doesn't copy the entire damn stream
        bytes_to_read = self.length
        buffer_size = 16 * 1024
        while bytes_to_read > 0:
            if bytes_to_read > buffer_size:
                handle.write(reader.handle.read(buffer_size))
                bytes_to_read -= buffer_size
            else:
                handle.write(reader.handle.read(bytes_to_read))
                bytes_to_read = 0


def extract(mst_path, out_path, ignore_existing):
    br = BinaryIO(open(mst_path, 'rb'))

    mst = MST()
    mst.read(br)

    try:
        os.makedirs(out_path, exist_ok=True)
    except OSError:
        raise Exception("Couldn't create output path.")

    for file in mst.files:
        file_out_path = os.path.join(out_path, file.name)
        if os.path.isfile(file_out_path) and ignore_existing:
            print('Skipping {0.name}'.format(file))
            continue

        print('Writing {0.name} ({0.length} bytes) originally created at {0.create_date}'.format(file))
        out_handle = open(file_out_path, 'wb')
        file.dump_contents(out_handle, br)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mst', help="path to the Metal Arms .MST file")
    parser.add_argument('path', help="directory to put the extracted files in")
    parser.add_argument('--ignore-existing', dest='ignore_existing', action='store_true')
    parser.set_defaults(ignore_existing=False)
    args = parser.parse_args()
    extract(args.mst, args.path, args.ignore_existing)
