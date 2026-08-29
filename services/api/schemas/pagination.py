from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number, 1-based index")
    size: int = Field(default=50, ge=1, le=100, description="Number of items per page")

class SortParams(BaseModel):
    sort_by: str | None = Field(default=None, description="Field to sort by")
    sort_desc: bool = Field(default=False, description="Sort in descending order")

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    size: int
    has_more: bool
