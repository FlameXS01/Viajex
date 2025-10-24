from enum import Enum
from dataclasses import dataclass

class UserRole(Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"

@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError("Email inválido")
    
    def _is_valid_email(self, email: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))