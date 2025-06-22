from pydantic import BaseModel

class Books(BaseModel):
    id: int
    title: str
    year: str
    score: int