from typing import Optional
from pydantic import BaseModel, EmailStr


# 共享属性
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None


# 创建用户时需要的属性
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str
    role_id: int
    team_id: Optional[int] = None


# 更新用户时可以更新的属性
class UserUpdate(UserBase):
    password: Optional[str] = None
    role_id: Optional[int] = None
    team_id: Optional[int] = None


# 数据库中存储的用户属性
class UserInDBBase(UserBase):
    id: int
    username: str
    
    class Config:
        from_attributes = True


# 返回给API的用户信息
class User(UserInDBBase):
    pass


# 数据库中存储的用户信息（包含哈希密码）
class UserInDB(UserInDBBase):
    hashed_password: str
