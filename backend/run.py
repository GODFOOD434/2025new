import uvicorn
import sys
import os
import time
import threading

# 添加当前目录到 Python 路径
# 这样可以在任何目录下运行该脚本
# 并且可以正确导入 app 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.init_db import create_tables, initialize_data

# 导入任务模块
from app.tasks import scheduled_tasks
from app.tasks.message_handlers import handle_inventory_message, handle_report_message

# 导入核心模块
from app.core.redis import get_redis
from app.core.rabbitmq import get_rabbitmq
from app.core.xxl_job import get_xxl_job


def setup_message_queues():
    """
    设置消息队列
    """
    # 获取 RabbitMQ 客户端
    rabbitmq = get_rabbitmq()

    # 声明队列
    rabbitmq.declare_queue("inventory_sync_result", durable=True)
    rabbitmq.declare_queue("report_generation_result", durable=True)

    # 声明交换机
    rabbitmq.declare_exchange("warehouse_workflow", exchange_type="direct", durable=True)

    # 绑定队列到交换机
    rabbitmq.bind_queue("inventory_sync_result", "warehouse_workflow", "inventory")
    rabbitmq.bind_queue("report_generation_result", "warehouse_workflow", "report")

    print("消息队列设置完成")


def setup_message_consumers():
    """
    设置消息消费者
    """
    # 获取 RabbitMQ 客户端
    rabbitmq = get_rabbitmq()

    # 设置库存消息消费者
    rabbitmq.setup_consumer("inventory_sync_result", handle_inventory_message, auto_ack=False)

    # 设置报表消息消费者
    rabbitmq.setup_consumer("report_generation_result", handle_report_message, auto_ack=False)

    print("消息消费者设置完成")


def start_message_consumers():
    """
    启动消息消费者
    """
    def run_consumer():
        # 获取 RabbitMQ 客户端
        rabbitmq = get_rabbitmq()

        # 启动消费
        rabbitmq.start_consuming()

    # 在新线程中启动消费者
    consumer_thread = threading.Thread(target=run_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()

    print("消息消费者启动完成")


def setup_scheduled_tasks():
    """
    设置定时任务
    """
    # 获取 XXL-Job 客户端
    xxl_job = get_xxl_job()

    # 注册到 XXL-Job Admin
    xxl_job.register_to_admin()

    # 添加本地定时任务
    xxl_job.add_local_job(
        job_name="syncInventoryTask",
        cron="0 0 * * *",  # 每天凌晨执行
        handler=scheduled_tasks.sync_inventory_task,
        params={"source": "local"}
    )

    xxl_job.add_local_job(
        job_name="generateReportTask",
        cron="0 1 * * *",  # 每天凌晨 1 点执行
        handler=scheduled_tasks.generate_report_task,
        params={"type": "daily", "source": "local"}
    )

    print("定时任务设置完成")


if __name__ == "__main__":
    # 创建数据库表
    create_tables()

    # 初始化数据
    initialize_data()

    # 设置消息队列
    try:
        setup_message_queues()
    except Exception as e:
        print(f"设置消息队列失败: {e}")

    # 设置定时任务
    try:
        setup_scheduled_tasks()
    except Exception as e:
        print(f"设置定时任务失败: {e}")

    # 设置消息消费者
    try:
        setup_message_consumers()
    except Exception as e:
        print(f"设置消息消费者失败: {e}")

    # 启动消息消费者
    try:
        start_message_consumers()
    except Exception as e:
        print(f"启动消息消费者失败: {e}")

    # 启动应用
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
