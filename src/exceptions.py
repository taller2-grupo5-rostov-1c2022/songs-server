class MessageException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.message = detail
        super().__init__(detail)
