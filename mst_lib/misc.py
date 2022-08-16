import struct


class ProtocolException(Exception):
    pass


class BinaryIO:
    def __init__(self, fh):
        self.handle = fh
        self.endian_prefix = '<'

    @property
    def pos(self):
        return self.handle.tell()

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
        return self.handle.read(length).decode('utf-8', 'backslashreplace')

    def seek(self, location):
        self.handle.seek(location)  # from start by default
