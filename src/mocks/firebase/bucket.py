class Blob:
    def __init__(self):
        self.data = None

    def download_as_bytes(self):
        assert self.data is not None
        return self.data

    def upload_from_string(self, data_string):
        self.data = data_string

    def delete(self):
        self.data = None


class Bucket:
    def __init__(self):
        self.files = {}

    def blob(self, file_id):
        if file_id not in self.files:
            self.files[file_id] = Blob()
        return self.files[file_id]


bucket = Bucket()
