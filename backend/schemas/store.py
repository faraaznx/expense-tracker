from pydantic import BaseModel


class StoreResponse(BaseModel):
    id: str
    name: str
    type: str
    logo_url: str | None
