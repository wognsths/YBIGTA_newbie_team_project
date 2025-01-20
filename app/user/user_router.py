from fastapi import APIRouter, HTTPException, Depends, status
from app.user.user_schema import User, UserLogin, UserUpdate, UserDeleteRequest
from app.user.user_service import UserService
from app.dependencies import get_user_service
from app.responses.base_response import BaseResponse

user = APIRouter(prefix="/api/user")

@user.post("/login", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def login_user(
    user_login: UserLogin, 
    service: UserService = Depends(get_user_service)
) -> BaseResponse[User]:
    """
    사용자의 이메일과 비밀번호를 이용해 로그인합니다.
    """
    try:
        user = service.login(user_login)
        return BaseResponse(status="success", data=user, message="Login Success.")
    except ValueError as e:
        if str(e) == "User not Found.":
            raise HTTPException(status_code=400, detail="User not Found.")
        elif str(e) == "Invalid ID/PW":
            raise HTTPException(status_code=400, detail="Invalid password.")
        else:
            raise HTTPException(status_code=400, detail="An unknown error occurred.")

@user.post("/register", response_model=BaseResponse[User], status_code=status.HTTP_201_CREATED)
def register_user(
    user: User, 
    service: UserService = Depends(get_user_service)
) -> BaseResponse[User]:
    """
    새로운 사용자를 등록합니다.
    """
    try:
        registered_user = service.register_user(user)
        return BaseResponse(status="success", data=registered_user, message="User Registered Successfully.")
    except ValueError as e:
        if str(e) == "User already Exists.":
            raise HTTPException(status_code=400, detail="User already Exists.")
        else:
            raise HTTPException(status_code=400, detail="An unknown error occurred.")

@user.delete("/delete", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def delete_user(
    user_delete_request: UserDeleteRequest, 
    service: UserService = Depends(get_user_service)
) -> BaseResponse[User]:
    """
    사용자의 이메일을 기반으로 사용자를 삭제합니다.
    """
    try:
        deleted_user = service.delete_user(user_delete_request.email)
        return BaseResponse(status="success", data=deleted_user, message="User Deletion Success.")
    except ValueError as e:
        if str(e) == "User not Found.":
            raise HTTPException(status_code=404, detail="User not Found.")
        else:
            raise HTTPException(status_code=400, detail="An unknown error occurred.")

@user.put("/update-password", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def update_user_password(
    user_update: UserUpdate, 
    service: UserService = Depends(get_user_service)
) -> BaseResponse[User]:
    """
    기존 사용자의 비밀번호를 업데이트합니다.
    """
    try:
        updated_user = service.update_user_pwd(user_update)
        return BaseResponse(status="success", data=updated_user, message="Password Updated Successfully.")
    except ValueError as e:
        if str(e) == "User not Found.":
            raise HTTPException(status_code=404, detail="User not Found.")
        else:
            raise HTTPException(status_code=400, detail="An unknown error occurred.")