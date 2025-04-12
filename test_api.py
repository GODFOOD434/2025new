import urllib.request
import json
import sys

def test_user_units_api():
    """测试获取用户单位API"""
    # 使用正确的API路径
    url = "http://localhost:8081/api/v1/purchase/user-units"
    
    try:
        print(f"正在请求API: {url}")
        req = urllib.request.Request(url)
        
        # 添加认证头（如果有的话）
        token = get_token()
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        
        # 发送请求
        with urllib.request.urlopen(req) as response:
            # 读取响应
            response_data = response.read().decode('utf-8')
            
            # 打印响应状态码和内容
            print(f"状态码: {response.status}")
            print(f"响应头: {response.headers}")
            
            if response.status == 200:
                data = json.loads(response_data)
                print("API响应成功:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return True
            else:
                print(f"API请求失败: {response_data}")
                return False
    except Exception as e:
        print(f"请求出错: {str(e)}")
        return False

def get_token():
    """获取访问令牌"""
    # 如果命令行参数中提供了令牌，则使用它
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    # 否则尝试登录获取令牌
    try:
        login_url = "http://localhost:8081/api/v1/login/access-token"
        
        # 创建登录请求
        login_data = json.dumps({
            "username": "admin@example.com",
            "password": "admin"
        }).encode('utf-8')
        
        req = urllib.request.Request(
            login_url,
            data=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        # 发送登录请求
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                token_data = json.loads(response.read().decode('utf-8'))
                return token_data.get("access_token")
            else:
                print(f"登录失败: {response.read().decode('utf-8')}")
                return None
    except Exception as e:
        print(f"登录出错: {str(e)}")
        return None

if __name__ == "__main__":
    print("开始测试用户单位API...")
    success = test_user_units_api()
    
    if success:
        print("测试成功!")
    else:
        print("测试失败!")
