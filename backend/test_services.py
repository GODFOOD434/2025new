"""
测试服务模块
"""

import sys
import os
import json
import time

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入核心模块
from app.core.redis import get_redis, set_key, get_key
from app.core.rabbitmq import get_rabbitmq, publish_message
from app.core.xxl_job import get_xxl_job
from app.tasks.scheduled_tasks import sync_inventory_task, generate_report_task


def test_redis():
    """
    测试 Redis 连接
    """
    print("\n===== 测试 Redis 连接 =====")
    
    try:
        # 获取 Redis 客户端
        redis_client = get_redis()
        
        # 设置测试键值
        test_data = {
            "name": "测试数据",
            "time": time.time(),
            "value": 123
        }
        
        set_key("test_key", test_data, expire=60)
        print("设置测试键值成功")
        
        # 获取测试键值
        result = get_key("test_key")
        print(f"获取测试键值成功: {result}")
        
        print("Redis 连接测试成功")
        return True
    except Exception as e:
        print(f"Redis 连接测试失败: {e}")
        return False


def test_rabbitmq():
    """
    测试 RabbitMQ 连接
    """
    print("\n===== 测试 RabbitMQ 连接 =====")
    
    try:
        # 获取 RabbitMQ 客户端
        rabbitmq = get_rabbitmq()
        
        # 声明测试队列
        rabbitmq.declare_queue("test_queue", durable=True)
        print("声明测试队列成功")
        
        # 发布测试消息
        test_message = {
            "name": "测试消息",
            "time": time.time(),
            "value": 456
        }
        
        publish_message("test_queue", test_message)
        print("发布测试消息成功")
        
        print("RabbitMQ 连接测试成功")
        return True
    except Exception as e:
        print(f"RabbitMQ 连接测试失败: {e}")
        return False


def test_xxl_job():
    """
    测试 XXL-Job 任务
    """
    print("\n===== 测试 XXL-Job 任务 =====")
    
    try:
        # 测试同步库存任务
        result1 = sync_inventory_task({"source": "test"})
        print(f"同步库存任务测试结果: {result1}")
        
        # 测试生成报表任务
        result2 = generate_report_task({"type": "test", "source": "test"})
        print(f"生成报表任务测试结果: {result2}")
        
        print("XXL-Job 任务测试成功")
        return True
    except Exception as e:
        print(f"XXL-Job 任务测试失败: {e}")
        return False


def main():
    """
    主函数
    """
    print("开始测试服务...")
    
    # 测试 Redis
    redis_result = test_redis()
    
    # 测试 RabbitMQ
    rabbitmq_result = test_rabbitmq()
    
    # 测试 XXL-Job
    xxl_job_result = test_xxl_job()
    
    # 输出测试结果
    print("\n===== 测试结果 =====")
    print(f"Redis 测试: {'成功' if redis_result else '失败'}")
    print(f"RabbitMQ 测试: {'成功' if rabbitmq_result else '失败'}")
    print(f"XXL-Job 测试: {'成功' if xxl_job_result else '失败'}")
    
    if redis_result and rabbitmq_result and xxl_job_result:
        print("\n所有服务测试通过！")
    else:
        print("\n部分服务测试失败，请检查配置和连接。")


if __name__ == "__main__":
    main()
