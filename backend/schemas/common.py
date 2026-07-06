from typing import Generic, TypeVar

from pydantic import BaseModel


DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    code: int
    data: DataT | None
    message: str


class CodeApiResponse(ApiResponse[DataT], Generic[DataT]):
    """Backward-compatible schema name for Milestone 8/9 routes."""


def success_response(data: DataT, message: str = "success") -> dict:
    return {
        "code": 200,
        "data": data,
        "message": message,
    }


def code_response(data: DataT, message: str = "success") -> dict:
    return success_response(data, message)
