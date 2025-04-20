from pydantic import BaseModel


class UsersPermissionsCreateSchema(BaseModel):
    user_id: int
    permission_id: int
