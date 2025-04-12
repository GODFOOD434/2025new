"""
测试 token 验证
"""

import sys
import os
import requests
import json
from urllib.parse import urljoin
import time

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 后端 API 地址
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

def test_token_validation():
    """
    测试 token 验证
    """
    print("\n===== 测试 token 验证 =====")
    
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
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        # 检查响应是否成功
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"获取到 token: {token}")
            
            # 解析 token
            import base64
            import json
            
            # 分割 token
            parts = token.split('.')
            if len(parts) != 3:
                print(f"Token 格式不正确: {token}")
                return
            
            # 解码 header
            header_b64 = parts[0]
            # 添加填充
            header_b64 += '=' * (4 - len(header_b64) % 4)
            header = json.loads(base64.b64decode(header_b64).decode('utf-8'))
            print(f"Token header: {header}")
            
            # 解码 payload
            payload_b64 = parts[1]
            # 添加填充
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.b64decode(payload_b64).decode('utf-8'))
            print(f"Token payload: {payload}")
            
            # 检查过期时间
            if 'exp' in payload:
                exp_time = payload['exp']
                current_time = int(time.time())
                print(f"当前时间: {current_time}, 过期时间: {exp_time}")
                print(f"Token 将在 {exp_time - current_time} 秒后过期")
            
            # 测试 token
            test_token(token)
            
            return token
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def test_token(token):
    """
    测试 token
    
    Args:
        token: 访问令牌
    """
    print("\n===== 测试 token =====")
    
    # 用户信息 URL
    user_info_url = urljoin(BASE_URL, f"{API_PREFIX}/users/me")
    print(f"用户信息 URL: {user_info_url}")
    
    # 测试不同的 Authorization 头格式
    headers_list = [
        {"Authorization": f"Bearer {token}"},
        {"Authorization": f"bearer {token}"},
        {"Authorization": f"Token {token}"},
        {"Authorization": token},
        {"Authorization": f"JWT {token}"}
    ]
    
    for i, headers in enumerate(headers_list):
        print(f"\n测试 Authorization 头格式 {i+1}: {headers}")
        
        try:
            # 发送请求
            response = requests.get(user_info_url, headers=headers)
            
            # 打印响应状态码和内容
            print(f"响应状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"响应内容: {response.text}")
                print("测试成功！")
            else:
                print(f"响应错误: {response.text}")
        except Exception as e:
            print(f"请求异常: {e}")

def main():
    """
    主函数
    """
    test_token_validation()

if __name__ == "__main__":
    main()
