from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """用户模型"""

    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # 角色关联
    role_id = Column(Integer, ForeignKey("wh_role.id"))
    role = relationship("Role", back_populates="users")

    # 团队关联
    team_id = Column(Integer, ForeignKey("wh_team.id"))
    team = relationship("Team", back_populates="members", foreign_keys=[team_id])


class Role(BaseModel):
    """角色模型"""

    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200))

    # 反向关联
    users = relationship("User", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role")


class Permission(BaseModel):
    """权限模型"""

    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200))
    code = Column(String(50), unique=True, nullable=False)

    # 反向关联
    roles = relationship("RolePermission", back_populates="permission")


class RolePermission(BaseModel):
    """角色权限关联模型"""

    role_id = Column(Integer, ForeignKey("wh_role.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("wh_permission.id"), primary_key=True)

    # 关联
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")


class Team(BaseModel):
    """团队模型"""

    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200))
    team_type = Column(String(20), nullable=False)  # 生产组、保管组、质检组

    # 团队领导
    leader_id = Column(Integer, ForeignKey("wh_user.id"))
    leader = relationship("User", foreign_keys=[leader_id])

    # 反向关联
    members = relationship("User", back_populates="team", foreign_keys="[User.team_id]")
