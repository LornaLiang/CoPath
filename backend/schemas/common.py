from typing import Generic, TypeVar

from pydantic import BaseModel


DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    success: bool
    data: DataT | None
    message: str


def success_response(data: DataT, message: str = "ok") -> dict:
    return {
        "success": True,
        "data": data,
        "message": message,
    }
