from pydantic import BaseModel


class TodoBase(BaseModel):
    title: str
    description: str
    done: bool = False # yangi
    user_id:int


class TodoCreate(TodoBase):
    pass


class TodoUpdate(TodoBase):
    pass


class TodoInDBBase(TodoBase):
    id: int

    class Config:
        from_attributes = True


class Todo(TodoInDBBase):
    pass