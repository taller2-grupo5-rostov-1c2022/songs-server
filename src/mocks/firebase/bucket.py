class Blob:
    def __init__(self):
        self.data = None
        self.public_url = "https://example.com"

    def download_as_bytes(self):
        assert self.data is not None
        return self.data

    def upload_from_string(self, data_string):
        self.data = data_string

    def upload_from_file(self, data):
        self.data = data

    def delete(self):
        self.data = None

    def make_public(self):
        pass

    def generate_signed_url(
        self, version, expiration, method
    ):  # pylint: disable=unused-argument

        return self.public_url

    def exists(self):
        return True


class Bucket:
    def __init__(self):
        self.files = {}

    def blob(self, file_id):
        if file_id not in self.files:
            self.files[file_id] = Blob()
        return self.files[file_id]


bucket_mock = Bucket()
