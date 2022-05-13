class Auth:
    def __init__(self):
        self.user = {}

    def update_user(self, uid, display_name=None, disabled=None):
        self.user["uid"] = uid
        self.user["display_name"] = display_name
        self.user["disabled"] = disabled
        return self.user


auth_mock = Auth()
