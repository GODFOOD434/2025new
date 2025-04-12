"""
XXL-Job 配置和工具模块
"""

import json
import time
import socket
import threading
import requests
from typing import Dict, Any, List, Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.config import settings


class XXLJob:
    """
    XXL-Job 客户端
    """
    
    def __init__(self):
        """
        初始化 XXL-Job 客户端
        """
        self.admin_url = settings.XXL_JOB_ADMIN_URL
        self.app_name = settings.XXL_JOB_APP_NAME
        self.token = settings.XXL_JOB_ACCESS_TOKEN
        
        # 本地任务注册表
        self.job_handlers = {}
        
        # 本地调度器
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        
        # 启动回调服务器
        self.callback_server = None
        if settings.XXL_JOB_ENABLE_CALLBACK:
            self.start_callback_server()
    
    def register_job_handler(self, job_name: str, handler: Callable):
        """
        注册任务处理器
        
        Args:
            job_name: 任务名称
            handler: 处理函数，接收 params 参数
        """
        self.job_handlers[job_name] = handler
        print(f"注册任务处理器: {job_name}")
    
    def execute_job(self, job_name: str, params: str) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            job_name: 任务名称
            params: 任务参数（JSON 字符串）
        
        Returns:
            执行结果
        """
        if job_name not in self.job_handlers:
            return {
                "code": 500,
                "msg": f"任务处理器 {job_name} 不存在"
            }
        
        try:
            # 解析参数
            if params and isinstance(params, str):
                try:
                    params_dict = json.loads(params)
                except:
                    params_dict = {"raw": params}
            else:
                params_dict = {}
            
            # 执行任务
            handler = self.job_handlers[job_name]
            result = handler(params_dict)
            
            return {
                "code": 200,
                "msg": "success",
                "data": result
            }
        except Exception as e:
            return {
                "code": 500,
                "msg": f"任务执行失败: {str(e)}"
            }
    
    def start_callback_server(self):
        """
        启动回调服务器
        """
        def run_server():
            import socket
            import json
            from http.server import HTTPServer, BaseHTTPRequestHandler
            
            class CallbackHandler(BaseHTTPRequestHandler):
                def do_POST(self):
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    
                    try:
                        data = json.loads(post_data.decode('utf-8'))
                        job_name = data.get('jobName')
                        params = data.get('params', '')
                        
                        # 验证 token
                        request_token = self.headers.get('XXL-JOB-ACCESS-TOKEN')
                        if request_token != settings.XXL_JOB_ACCESS_TOKEN:
                            response = {
                                "code": 500,
                                "msg": "Invalid token"
                            }
                        else:
                            # 执行任务
                            response = xxl_job_client.execute_job(job_name, params)
                    except Exception as e:
                        response = {
                            "code": 500,
                            "msg": f"Error: {str(e)}"
                        }
                    
                    # 返回响应
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            
            # 启动 HTTP 服务器
            server_address = ('', settings.XXL_JOB_CALLBACK_PORT)
            httpd = HTTPServer(server_address, CallbackHandler)
            print(f"XXL-Job 回调服务器启动在端口 {settings.XXL_JOB_CALLBACK_PORT}")
            httpd.serve_forever()
        
        # 在新线程中启动服务器
        self.callback_server = threading.Thread(target=run_server)
        self.callback_server.daemon = True
        self.callback_server.start()
    
    def register_to_admin(self):
        """
        向 XXL-Job Admin 注册执行器
        """
        if not self.admin_url:
            print("XXL-Job Admin URL 未配置，跳过注册")
            return
        
        # 获取本机 IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "127.0.0.1"
        
        # 注册参数
        data = {
            "appName": self.app_name,
            "title": f"{self.app_name} Executor",
            "addressType": 0,  # 自动注册
            "addresses": f"http://{ip}:{settings.XXL_JOB_CALLBACK_PORT}"
        }
        
        # 发送注册请求
        headers = {
            "XXL-JOB-ACCESS-TOKEN": self.token
        }
        
        try:
            response = requests.post(
                f"{self.admin_url}/api/registry",
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    print("XXL-Job 执行器注册成功")
                else:
                    print(f"XXL-Job 执行器注册失败: {result.get('msg')}")
            else:
                print(f"XXL-Job 执行器注册失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"XXL-Job 执行器注册失败: {e}")
    
    def add_local_job(self, job_name: str, cron: str, handler: Callable, params: Dict[str, Any] = None):
        """
        添加本地定时任务
        
        Args:
            job_name: 任务名称
            cron: cron 表达式
            handler: 处理函数
            params: 任务参数
        """
        # 注册任务处理器
        self.register_job_handler(job_name, handler)
        
        # 添加定时任务
        self.scheduler.add_job(
            func=lambda: handler(params or {}),
            trigger=CronTrigger.from_crontab(cron),
            id=job_name,
            replace_existing=True
        )
        
        print(f"添加本地定时任务: {job_name}, cron: {cron}")


# 单例模式
xxl_job_client = XXLJob()


def get_xxl_job() -> XXLJob:
    """
    获取 XXL-Job 客户端
    """
    return xxl_job_client


def register_job_handler(job_name: str):
    """
    注册任务处理器的装饰器
    
    Args:
        job_name: 任务名称
    """
    def decorator(func):
        xxl_job_client.register_job_handler(job_name, func)
        return func
    return decorator
