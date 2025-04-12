"""
定时任务模块
"""

import time
from datetime import datetime
from app.core.xxl_job import register_job_handler
from app.core.redis import set_key, get_key
from app.core.rabbitmq import publish_message


@register_job_handler("syncInventoryTask")
def sync_inventory_task(params):
    """
    同步库存任务
    
    Args:
        params: 任务参数
    
    Returns:
        任务执行结果
    """
    print(f"执行同步库存任务，参数: {params}")
    
    # 记录任务执行时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 模拟任务执行
    time.sleep(1)
    
    # 将结果存入 Redis
    result = {
        "task": "syncInventoryTask",
        "time": now,
        "params": params,
        "status": "success"
    }
    
    set_key("last_sync_inventory", result, expire=3600)
    
    # 发送消息到队列
    publish_message("inventory_sync_result", result)
    
    return {
        "success": True,
        "time": now,
        "message": "库存同步完成"
    }


@register_job_handler("generateReportTask")
def generate_report_task(params):
    """
    生成报表任务
    
    Args:
        params: 任务参数
    
    Returns:
        任务执行结果
    """
    print(f"执行生成报表任务，参数: {params}")
    
    # 记录任务执行时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 获取报表类型
    report_type = params.get("type", "daily")
    
    # 模拟任务执行
    time.sleep(2)
    
    # 将结果存入 Redis
    result = {
        "task": "generateReportTask",
        "time": now,
        "type": report_type,
        "status": "success"
    }
    
    set_key(f"last_report_{report_type}", result, expire=3600)
    
    # 发送消息到队列
    publish_message("report_generation_result", result)
    
    return {
        "success": True,
        "time": now,
        "type": report_type,
        "message": f"{report_type} 报表生成完成"
    }
