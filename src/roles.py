from fastapi import HTTPException, Header

ROLES_TABLE = {"listener": 0, "artist": 1, "admin": 2}


class Role:
    def __init__(self, role_name):
        if role_name is None:
            self.role_value = ROLES_TABLE["listener"]
        elif role_name not in ROLES_TABLE:
            raise HTTPException(status_code=422, detail=f"Invalid role: {role_name}")
        self.role_value = ROLES_TABLE[role_name]

    @classmethod
    def admin(cls):
        return cls("admin")

    def __lt__(self, other):
        return self.role_value < other.role_value

    def __eq__(self, other):
        return self.role_value == other.role_value

    def can_edit_everything(self):
        return self == Role.admin()

    def can_see_blocked(self):
        return self == Role.admin()

    def can_block(self):
        return self == Role.admin()


async def get_role(role_name: str = Header("listener")):
    return Role(role_name)
