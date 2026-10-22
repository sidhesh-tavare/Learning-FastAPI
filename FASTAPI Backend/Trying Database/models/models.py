from pydantic import BaseModel

class TaskCreate(BaseModel):
    title : str 
    description : str | None = None

class TaskUpdate(BaseModel):
    is_completed : bool
    updated_desc : str