class Loader:
    def __init__(self, entry):
        self.entry = entry

    def export(self, handle, reader):
        reader.seek(self.entry.location)

        # kind of like shutil.copyfileobj, but doesn't copy the entire damn stream
        bytes_to_read = self.entry.length

        buffer_size = 16 * 1024
        while bytes_to_read > 0:
            if bytes_to_read > buffer_size:
                handle.write(reader.handle.read(buffer_size))
                bytes_to_read -= buffer_size
            else:
                handle.write(reader.handle.read(bytes_to_read))
                bytes_to_read = 0
