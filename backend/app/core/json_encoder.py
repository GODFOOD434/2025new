import json
import math
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy.ext.declarative import DeclarativeMeta


class CustomJSONEncoder(json.JSONEncoder):
    """
    自定义JSON编码器，处理特殊类型和值
    """
    def default(self, obj: Any) -> Any:
        # 处理日期和时间
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        
        # 处理枚举
        if isinstance(obj, Enum):
            return obj.value
        
        # 处理Decimal
        if isinstance(obj, Decimal):
            return float(obj)
        
        # 处理SQLAlchemy模型
        if isinstance(obj.__class__, DeclarativeMeta):
            return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        
        # 处理NaN和无穷大
        if isinstance(obj, float):
            if math.isnan(obj):
                return 0.0  # 将NaN替换为0
            if math.isinf(obj):
                return float("1e100") if obj > 0 else float("-1e100")  # 将无穷大替换为非常大的数
        
        return super().default(obj)


def custom_json_dumps(obj: Any, **kwargs) -> str:
    """
    使用自定义编码器将对象转换为JSON字符串
    """
    return json.dumps(obj, cls=CustomJSONEncoder, **kwargs)
