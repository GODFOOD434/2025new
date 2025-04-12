"""
测试登录 API
"""

import sys
import os
import requests
from urllib.parse import urljoin

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 后端 API 地址
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

def test_login():
    """
    测试登录 API
    """
    print("\n===== 测试登录 API =====")
    
    # 登录 URL
    login_url = urljoin(BASE_URL, f"{API_PREFIX}/login/access-token")
    print(f"登录 URL: {login_url}")
    
    # 登录凭证
    credentials = {
        "username": "admin",
        "password": "admin"
    }
    
    try:
        # 发送登录请求
        response = requests.post(
            login_url,
            data=credentials,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # 打印响应状态码和内容
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 检查响应是否成功
        if response.status_code == 200:
            data = response.json()
            print(f"登录成功，获取到 token: {data.get('access_token')}")
            return data.get('access_token')
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def test_get_user_info(token):
    """
    测试获取用户信息 API
    
    Args:
        token: 访问令牌
    """
    if not token:
        print("没有有效的 token，跳过测试")
        return
    
    print("\n===== 测试获取用户信息 API =====")
    
    # 用户信息 URL
    user_info_url = urljoin(BASE_URL, f"{API_PREFIX}/users/me")
    print(f"用户信息 URL: {user_info_url}")
    
    try:
        # 发送请求
        response = requests.get(
            user_info_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 打印响应状态码和内容
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 检查响应是否成功
        if response.status_code == 200:
            data = response.json()
            print(f"获取用户信息成功: {data}")
        else:
            print(f"获取用户信息失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

def main():
    """
    主函数
    """
    # 测试登录
    token = test_login()
    
    # 测试获取用户信息
    test_get_user_info(token)

if __name__ == "__main__":
    main()
