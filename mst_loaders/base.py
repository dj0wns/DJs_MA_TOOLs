class Loader:
    def __init__(self, entry):
        self.entry = entry
        self.data = None

    def read(self, reader):
        reader.seek(self.entry.location)
        self.data = reader.handle.read(self.entry.length)

    def write(self, writer):
        self.entry.location = writer.tell()
        writer.handle.write(self.data)
        self.entry.length = writer.tell() - self.entry.location

    def save(self, handle):
        handle.write(self.data)

    def load(self, handle):
        self.data = handle.read()
