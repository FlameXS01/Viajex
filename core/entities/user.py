from dataclasses import dataclass, field
from datetime import datetime
from typing import  Optional
from .value_objects import Email, UserRole

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    email: Email = field(default_factory=lambda: Email(f"default{id}@example.com"))
    role: UserRole = UserRole.USER
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def can_manage_users(self) -> bool:
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]
    
    def can_liquidate_diets(self) -> bool:
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.USER]
    
    def can_config_app(self) -> bool:
        return self.role in [UserRole.ADMIN]