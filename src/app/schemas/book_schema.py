from pydantic import BaseModel


class BookSchema(BaseModel):
    id: int
    title: str
    price: float
    rating: float
    avaliability: bool
    category: str
    image: str

    class Config:
        orm_mode = True
