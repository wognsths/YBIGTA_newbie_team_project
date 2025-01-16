from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate
from app.responses.base_response import BaseResponse
from typing import Optional

class UserService:
    def __init__(self, userRepository: UserRepository) -> None:
        """
        UserService를 초기화합니다. UserRepository를 이용해 데이터 처리합니다.

        Args:
            userRepository (UserRepository): 사용자 데이터를 저장하고 조회하는 리포지토리.
        """
        self.repo = userRepository

    def login(self, user_login: UserLogin) -> User:
        """
        사용자의 이메일과 비밀번호를 이용해 인증을 처리합니다.

        Args:
            user_login (UserLogin): 사용자 로그인 정보 (이메일, 비밀번호).

        Raises:
            ValueError: 이메일 또는 비밀번호가 잘못된 경우.

        Returns:
            User: 인증된 사용자 객체.
        """
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            raise ValueError("User not Found.")
        if user.password != user_login.password:
            raise ValueError("Invalid ID/PW")
        return user

    def register_user(self, new_user: User) -> User:
        """
        새로운 사용자를 시스템에 등록합니다.

        Args:
            new_user (User): 등록할 사용자 정보.

        Raises:
            ValueError: 이미 등록된 이메일이 있는 경우.

        Returns:
            User: 등록된 사용자 객체.
        """
        existing_user = self.repo.get_user_by_email(new_user.email)
        if existing_user:
            raise ValueError("User already Exists.")
        return self.repo.save_user(new_user)

    def delete_user(self, email: str) -> User:
        """
        사용자의 이메일을 기반으로 사용자를 삭제합니다.

        Args:
            email (str): 삭제할 사용자의 이메일.

        Raises:
            ValueError: 사용자를 찾을 수 없는 경우.

        Returns:
            User: 삭제된 사용자 객체.
        """
        user = self.repo.get_user_by_email(email)
        if not user:
            raise ValueError("User not Found.")
        return self.repo.delete_user(user)

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        """
        기존 사용자의 비밀번호를 업데이트합니다.

        Args:
            user_update (UserUpdate): 비밀번호를 업데이트할 사용자 정보 (이메일, 새로운 비밀번호).

        Raises:
            ValueError: 사용자가 없거나 비밀번호가 유효하지 않은 경우.

        Returns:
            User: 비밀번호가 업데이트된 사용자 객체.
        """
        user = self.repo.get_user_by_email(user_update.email)
        if not user:
            raise ValueError("User not Found.")
        user.password = user_update.new_password
        return self.repo.save_user(user)