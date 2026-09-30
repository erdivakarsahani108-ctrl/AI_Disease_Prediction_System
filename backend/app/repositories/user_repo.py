"""User repository — DB access layer."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, **kwargs) -> User:
        for k, v in kwargs.items():
            if v is not None and hasattr(user, k):
                setattr(user, k, v)
        self.db.commit()
        self.db.refresh(user)
        return user
