from pydantic import BaseModel

class ProjectBase(BaseModel):
    name: str
    description: str | None = None


class ProjectRead(ProjectBase):
    id: int
    organization_id: int | None = None
    
    class Config:
        from_attributes = True
