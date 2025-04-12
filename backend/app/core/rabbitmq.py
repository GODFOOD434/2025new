"""
RabbitMQ 配置和工具模块
"""

import json
import pika
from typing import Any, Optional, Callable, Dict
from app.core.config import settings


class RabbitMQ:
    """
    RabbitMQ 客户端
    """

    def __init__(self):
        """
        初始化 RabbitMQ 连接
        """
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        """
        连接到 RabbitMQ 服务器
        """
        try:
            # 创建连接参数
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )

            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                virtual_host=settings.RABBITMQ_VHOST,
                credentials=credentials
            )

            # 建立连接
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            print("RabbitMQ 连接成功")
        except Exception as e:
            print(f"RabbitMQ 连接失败: {e}")

    def close(self):
        """
        关闭 RabbitMQ 连接
        """
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("RabbitMQ 连接已关闭")

    def declare_queue(self, queue_name: str, durable: bool = True):
        """
        声明队列

        Args:
            queue_name: 队列名称
            durable: 是否持久化
        """
        if not self.channel:
            self.connect()

        self.channel.queue_declare(queue=queue_name, durable=durable)

    def declare_exchange(self, exchange_name: str, exchange_type: str = 'direct', durable: bool = True):
        """
        声明交换机

        Args:
            exchange_name: 交换机名称
            exchange_type: 交换机类型，可选值为 direct, fanout, topic, headers
            durable: 是否持久化
        """
        if not self.channel:
            self.connect()

        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=durable
        )

    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str = ''):
        """
        绑定队列到交换机

        Args:
            queue_name: 队列名称
            exchange_name: 交换机名称
            routing_key: 路由键
        """
        if not self.channel:
            self.connect()

        self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )

    def publish(self, exchange: str, routing_key: str, body: Any, properties: Optional[pika.BasicProperties] = None):
        """
        发布消息

        Args:
            exchange: 交换机名称
            routing_key: 路由键
            body: 消息内容（将自动序列化为 JSON）
            properties: 消息属性
        """
        if not self.channel:
            self.connect()

        # 序列化消息
        if not isinstance(body, str):
            body = json.dumps(body, ensure_ascii=False)

        # 设置默认属性
        if properties is None:
            properties = pika.BasicProperties(
                delivery_mode=2,  # 持久化消息
                content_type='application/json'
            )

        # 发布消息
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=properties
        )

    def setup_consumer(self, queue: str, callback: Callable, auto_ack: bool = True):
        """
        设置消费者（不启动消费）

        Args:
            queue: 队列名称
            callback: 回调函数，接收 channel, method, properties, body 四个参数
            auto_ack: 是否自动确认
        """
        if not self.channel:
            self.connect()

        self.channel.basic_consume(
            queue=queue,
            on_message_callback=callback,
            auto_ack=auto_ack
        )

        print(f"成功设置队列 {queue} 的消费者")

    def start_consuming(self):
        """
        启动消费（阻塞方法）
        """
        if not self.channel:
            self.connect()

        print("开始消费消息，按 CTRL+C 退出")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            print("消费已停止")
        except Exception as e:
            print(f"消费过程中发生错误: {e}")
            self.channel.stop_consuming()


# 单例模式
rabbitmq_client = RabbitMQ()


def get_rabbitmq() -> RabbitMQ:
    """
    获取 RabbitMQ 客户端
    """
    return rabbitmq_client


def publish_message(queue: str, message: Any, exchange: str = '', routing_key: str = None):
    """
    发布消息到队列

    Args:
        queue: 队列名称
        message: 消息内容
        exchange: 交换机名称，默认为空（使用默认交换机）
        routing_key: 路由键，默认为队列名称
    """
    if routing_key is None:
        routing_key = queue

    # 确保队列存在
    rabbitmq_client.declare_queue(queue)

    # 发布消息
    rabbitmq_client.publish(
        exchange=exchange,
        routing_key=routing_key,
        body=message
    )

    return True
