from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import User, Role, Permission, Team
from app.db.session import Base, engine
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """初始化数据库"""
    
    # 创建角色
    roles = {
        "admin": "系统管理员",
        "leader": "中心领导",
        "production_leader": "生产组长",
        "production_staff": "生产组员工",
        "keeper_leader": "保管组长",
        "keeper": "保管员",
        "inspector_leader": "质检组长",
        "inspector": "质检员",
        "user_unit_contact": "用户单位联系人"
    }
    
    for role_code, role_name in roles.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name, description=f"{role_name}角色")
            db.add(role)
    
    # 创建团队
    teams = {
        "production": "生产组",
        "keeper": "保管组",
        "inspector": "质检组"
    }
    
    for team_code, team_name in teams.items():
        team = db.query(Team).filter(Team.name == team_name).first()
        if not team:
            team = Team(name=team_name, description=f"{team_name}", team_type=team_code)
            db.add(team)
    
    # 提交更改
    db.commit()
    
    # 创建超级管理员用户（如果不存在）
    admin_role = db.query(Role).filter(Role.name == "系统管理员").first()
    admin = db.query(User).filter(User.username == "admin").first()
    
    if not admin and admin_role:
        from app.core.security import get_password_hash
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            full_name="系统管理员",
            is_active=True,
            is_superuser=True,
            role_id=admin_role.id
        )
        db.add(admin)
        db.commit()


def create_tables():
    """创建所有表"""
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully.")


def initialize_data():
    """初始化数据"""
    from app.db.session import SessionLocal
    
    db = SessionLocal()
    try:
        logger.info("Initializing data...")
        init_db(db)
        logger.info("Data initialized successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    initialize_data()
