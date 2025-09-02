from pydantic import BaseModel

class OrganizationBase(BaseModel):
    name: str

class OrganizationRead(OrganizationBase):
    id: int

    class Config:
        from_attributes = True
