@echo off
echo 正在创建虚拟环境...
python -m venv venv

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 升级 pip...
python -m pip install --upgrade pip

echo 安装依赖...
pip install -e .

echo 安装完成！
echo 使用 "venv\Scripts\activate.bat" 激活虚拟环境
echo 使用 "python run.py" 启动应用
