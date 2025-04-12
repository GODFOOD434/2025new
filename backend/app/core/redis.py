"""
Redis 配置和工具模块
"""

import json
from typing import Any, Optional, Union, Dict, List
import redis
from redis.connection import ConnectionPool
from app.core.config import settings

# Redis 连接池
redis_pool = ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

# Redis 客户端
redis_client = redis.Redis(connection_pool=redis_pool)


def get_redis() -> redis.Redis:
    """
    获取 Redis 客户端
    """
    return redis_client


def set_key(key: str, value: Any, expire: int = None) -> bool:
    """
    设置 Redis 键值
    
    Args:
        key: 键名
        value: 值（将自动序列化为 JSON）
        expire: 过期时间（秒），None 表示永不过期
        
    Returns:
        是否成功
    """
    try:
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)
        redis_client.set(key, value, ex=expire)
        return True
    except Exception as e:
        print(f"Redis set error: {e}")
        return False


def get_key(key: str, default: Any = None) -> Any:
    """
    获取 Redis 键值
    
    Args:
        key: 键名
        default: 默认值
        
    Returns:
        键值（如果是 JSON 将自动反序列化）
    """
    try:
        value = redis_client.get(key)
        if value is None:
            return default
        
        # 尝试解析 JSON
        try:
            return json.loads(value)
        except:
            return value
    except Exception as e:
        print(f"Redis get error: {e}")
        return default


def delete_key(key: str) -> bool:
    """
    删除 Redis 键
    
    Args:
        key: 键名
        
    Returns:
        是否成功
    """
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Redis delete error: {e}")
        return False


def set_hash(name: str, key: str, value: Any) -> bool:
    """
    设置 Redis 哈希表字段
    
    Args:
        name: 哈希表名
        key: 字段名
        value: 值（将自动序列化为 JSON）
        
    Returns:
        是否成功
    """
    try:
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)
        redis_client.hset(name, key, value)
        return True
    except Exception as e:
        print(f"Redis hset error: {e}")
        return False


def get_hash(name: str, key: str, default: Any = None) -> Any:
    """
    获取 Redis 哈希表字段
    
    Args:
        name: 哈希表名
        key: 字段名
        default: 默认值
        
    Returns:
        字段值（如果是 JSON 将自动反序列化）
    """
    try:
        value = redis_client.hget(name, key)
        if value is None:
            return default
        
        # 尝试解析 JSON
        try:
            return json.loads(value)
        except:
            return value
    except Exception as e:
        print(f"Redis hget error: {e}")
        return default


def get_hash_all(name: str) -> Dict[str, Any]:
    """
    获取 Redis 哈希表所有字段
    
    Args:
        name: 哈希表名
        
    Returns:
        所有字段（如果是 JSON 将自动反序列化）
    """
    try:
        result = {}
        data = redis_client.hgetall(name)
        
        for key, value in data.items():
            # 尝试解析 JSON
            try:
                result[key] = json.loads(value)
            except:
                result[key] = value
                
        return result
    except Exception as e:
        print(f"Redis hgetall error: {e}")
        return {}
