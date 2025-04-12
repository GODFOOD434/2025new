from setuptools import setup, find_packages
import sys

# 根据 Python 版本确定依赖项
install_requires = [
    "fastapi>=0.68.0,<0.69.0",
    "pydantic>=1.8.0,<2.0.0",
    "uvicorn>=0.15.0,<0.16.0",
    "sqlalchemy>=1.4.0,<1.5.0",
    "psycopg2-binary>=2.9.1,<3.0.0",
    "python-jose[cryptography]>=3.3.0,<4.0.0",
    "passlib[bcrypt]>=1.7.4,<2.0.0",
    "python-multipart>=0.0.5,<0.1.0",
    "email-validator>=1.1.3,<2.0.0",
    "python-dotenv>=0.19.0,<0.20.0",
    "openpyxl>=3.0.9,<4.0.0",
    "pytest>=6.2.5,<7.0.0",
    "httpx>=0.19.0,<0.20.0",
]

# 对于 Python 3.13，使用 polars 替代 pandas
if sys.version_info >= (3, 13):
    install_requires.append("polars>=0.20.0")
else:
    install_requires.append("pandas>=1.5.3,<2.0.0")

setup(
    name="warehouse_workflow",
    version="0.1.0",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.8",
    description="仓储工作流系统后端",
    author="Your Name",
    author_email="your.email@example.com",
)
