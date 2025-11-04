from pydantic import BaseModel, Field
from typing import Optional

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page")
    ordering: Optional[str] = Field(None, description="Field to sort by")
    ordering_desc: bool = Field(False, description="Whether to sort descending")
    filter_field: Optional[str] = Field(None, description="Field to filter by")
    filter_value: Optional[str] = Field(None, description="Value to filter by")

    @property
    def filters(self) -> Optional[list[tuple[str, str]]]:
        if self.filter_field and self.filter_value:
            return [(self.filter_field, self.filter_value)]
        return None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    
class PaginationResponse(BaseModel):
    total: int
    items: list
    
    class Config:
        from_attributes = True