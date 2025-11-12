from pydantic import BaseModel


class Category(BaseModel):
    id: str
    name: str
    description: str

    class Config:
        from_attributes = True