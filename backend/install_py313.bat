@echo off
echo Installing dependencies for Python 3.13...

echo Installing polars (alternative to pandas)...
pip install polars>=0.20.0

echo Installing other dependencies...
pip install fastapi>=0.68.0,<0.69.0
pip install pydantic>=1.8.0,<2.0.0
pip install pydantic-settings>=2.0.0
pip install uvicorn>=0.15.0,<0.16.0
pip install sqlalchemy>=1.4.0,<1.5.0
pip install psycopg2-binary>=2.9.1,<3.0.0
pip install python-jose[cryptography]>=3.3.0,<4.0.0
pip install passlib[bcrypt]>=1.7.4,<2.0.0
pip install python-multipart>=0.0.5,<0.1.0
pip install email-validator>=2.0.0
pip install python-dotenv>=0.19.0,<0.20.0
pip install openpyxl>=3.0.9,<4.0.0
pip install pytest>=6.2.5,<7.0.0
pip install httpx>=0.19.0,<0.20.0

echo Installing Redis dependencies...
pip install redis>=4.3.4
pip install aioredis>=2.0.1

echo Installing Message Queue dependencies...
pip install pika>=1.3.0
pip install celery>=5.2.7

echo Installing XXL-Job dependencies...
pip install requests>=2.28.1
pip install apscheduler>=3.9.1

echo Installation complete!
echo.
echo To run the application, use: python run.py
