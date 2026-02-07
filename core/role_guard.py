from enum import Enum

class UserRole(Enum):
    DEVELOPER = "developer"
    USER = "user"

def check_role(user_role: str, allowed_roles: list[str]) -> bool:
    return user_role in allowed_roles
