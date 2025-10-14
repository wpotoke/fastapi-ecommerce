from typing import Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str, headers: Optional[dict] = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(AppException):
    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        detail: str = "Resource not found",
    ):
        super().__init__(status_code=status_code, detail=detail)


class ConflictException(AppException):
    def __init__(
        self,
        status_code: int = status.HTTP_409_CONFLICT,
        detail: str = "Resource already exists",
    ):
        super().__init__(status_code=status_code, detail=detail)


class BusinessException(AppException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: str = "Not authorized",
    ):
        super().__init__(status_code=status_code, detail=detail)
