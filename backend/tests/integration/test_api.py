import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.models.user import User, Role
from app.core.security import get_password_hash


# 创建内存数据库用于测试
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 替换依赖项
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


class TestAPI(unittest.TestCase):
    """API集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试前设置"""
        # 创建表
        Base.metadata.create_all(bind=engine)
        
        # 创建测试数据
        db = TestingSessionLocal()
        
        # 创建角色
        admin_role = Role(name="系统管理员", description="系统管理员")
        db.add(admin_role)
        db.commit()
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            full_name="系统管理员",
            is_active=True,
            is_superuser=True,
            role_id=admin_role.id
        )
        db.add(admin_user)
        db.commit()
        
        db.close()
    
    @classmethod
    def tearDownClass(cls):
        """测试后清理"""
        # 删除表
        Base.metadata.drop_all(bind=engine)
    
    def setUp(self):
        """每个测试前设置"""
        self.client = TestClient(app)
        
        # 登录获取token
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        response = self.client.post("/api/v1/login/access-token", data=login_data)
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_read_main(self):
        """测试主页"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "欢迎使用仓储工作流系统API"})
    
    def test_login(self):
        """测试登录"""
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        response = self.client.post("/api/v1/login/access-token", data=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertEqual(response.json()["token_type"], "bearer")
    
    def test_read_users_me(self):
        """测试获取当前用户"""
        response = self.client.get("/api/v1/users/me", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "admin")
        self.assertEqual(response.json()["email"], "admin@example.com")
        self.assertEqual(response.json()["full_name"], "系统管理员")
        self.assertTrue(response.json()["is_active"])
        self.assertTrue(response.json()["is_superuser"])


if __name__ == "__main__":
    unittest.main()
