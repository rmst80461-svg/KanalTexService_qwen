"""
Web services for the admin panel
"""
from flask_login import UserMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.database import Database


class User(UserMixin):
    def __init__(self, id: int):
        self.id = id


def load_user(user_id: str) -> User:
    """Load user for Flask-Login"""
    return User(int(user_id))