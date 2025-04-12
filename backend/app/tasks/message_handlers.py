"""
消息处理模块
"""

import json
from typing import Dict, Any
from app.core.redis import set_key


def handle_inventory_message(ch, method, properties, body):
    """
    处理库存消息
    
    Args:
        ch: 通道
        method: 方法
        properties: 属性
        body: 消息内容
    """
    try:
        # 解析消息
        message = json.loads(body)
        print(f"收到库存消息: {message}")
        
        # 处理消息
        process_inventory_message(message)
        
        # 确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"处理库存消息失败: {e}")
        # 拒绝消息并重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def handle_report_message(ch, method, properties, body):
    """
    处理报表消息
    
    Args:
        ch: 通道
        method: 方法
        properties: 属性
        body: 消息内容
    """
    try:
        # 解析消息
        message = json.loads(body)
        print(f"收到报表消息: {message}")
        
        # 处理消息
        process_report_message(message)
        
        # 确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"处理报表消息失败: {e}")
        # 拒绝消息并重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def process_inventory_message(message: Dict[str, Any]):
    """
    处理库存消息
    
    Args:
        message: 消息内容
    """
    # 将消息存入 Redis
    set_key("last_inventory_message", message, expire=3600)
    
    # 模拟处理逻辑
    print(f"处理库存消息: {message}")


def process_report_message(message: Dict[str, Any]):
    """
    处理报表消息
    
    Args:
        message: 消息内容
    """
    # 将消息存入 Redis
    set_key("last_report_message", message, expire=3600)
    
    # 模拟处理逻辑
    print(f"处理报表消息: {message}")
