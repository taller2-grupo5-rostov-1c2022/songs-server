class DocumentMock:
    def __init__(self, document_id):
        self.id = str(document_id)
        self.entry = None
        self.exists = False

    def set(self, entry):
        self.entry = entry
        self.exists = True

    def get(self):
        return self

    def update(self, entry):
        if not self.exists:
            raise FileNotFoundError
        self.entry = entry

    def delete(self):
        self.entry = None
        self.exists = False

    def to_dict(self):
        return self.entry


class CollectionMock:
    def __init__(self):
        self.doc_name_id_counter = 0
        self.documents = {}

    def document(self, name=None):
        if name is None:
            self.doc_name_id_counter += 1
            self.documents[str(self.doc_name_id_counter)] = DocumentMock(
                self.doc_name_id_counter
            )
            return self.documents[str(self.doc_name_id_counter)]

        if name not in self.documents:
            self.documents[name] = DocumentMock(name)
        return self.documents[name]

    def stream(self):
        return self.documents.values()


class DBMock:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        return self.collections[name]


db = DBMock()
db.collections["songs"] = CollectionMock()
