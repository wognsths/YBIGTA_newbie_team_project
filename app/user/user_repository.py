# app/user/user_repository.py
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import Column, String

from database.mysql_connection import Base
from app.user.user_schema import User


class UserTable(Base):
    __tablename__ = "users"
    email = Column(String(255), primary_key=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False)


class UserRepository:
    def __init__(self, db: Session) -> None:
        """
        - DB(Session)로 관리
        - db: SQLAlchemy Session (FastAPI Dependencies에서 주입)
        """
        self.db = db

    def _to_user(self, user_row: UserTable) -> User:
        """
        SQLAlchemy UserTable 인스턴스의 필드만 추출하여 Pydantic User 모델로 변환
        """
        return User.model_validate({
            "email": user_row.email,
            "username": user_row.username,
            "password": user_row.password,
        })

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        email로 DB에서 조회  
         - 조회 결과가 없으면 None 반환  
         - 있으면 Pydantic User로 변환하여 반환
        """
        user_row = (
            self.db.query(UserTable)
            .filter(UserTable.email == email)
            .first()
        )
        if not user_row:
            return None
        return self._to_user(user_row)

    def save_user(self, user: User) -> User:
        """
        - 같은 email이 이미 존재하면 UPDATE  
        - 없으면 INSERT  
        변환 후 Pydantic User 인스턴스를 반환
        """
        existing = (
            self.db.query(UserTable)
            .filter(UserTable.email == user.email)
            .first()
        )
        if existing:
            # UPDATE
            existing.username = user.username
            existing.password = user.password
            self.db.commit()
            self.db.refresh(existing)
            return self._to_user(existing)

        # INSERT
        new_user = UserTable(
            email=user.email,
            username=user.username,
            password=user.password,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return self._to_user(new_user)

    def delete_user(self, user: User) -> User:
        """
        user.email로 찾아 삭제  
         - 해당 사용자가 없으면 ValueError 발생  
         - 삭제한 후의 데이터를 Pydantic User로 반환
        """
        user_row = (
            self.db.query(UserTable)
            .filter(UserTable.email == user.email)
            .first()
        )
        if not user_row:
            raise ValueError(f"No user found with email: {user.email}")

        self.db.delete(user_row)
        self.db.commit()
        return self._to_user(user_row)
