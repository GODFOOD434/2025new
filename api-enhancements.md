# API增强设计

## 1. 采购订单管理API

### 1.1 Excel导入API
```
POST /api/purchase/import
请求：multipart/form-data 格式的Excel文件
响应：
{
  "success": true,
  "data": {
    "totalCount": 100,
    "successCount": 98,
    "errorCount": 2,
    "errorDetails": [
      {
        "rowIndex": 5,
        "errorMessage": "采购订单号不能为空"
      },
      {
        "rowIndex": 10,
        "errorMessage": "申请数量必须大于0"
      }
    ],
    "importId": "IMP20230615001"
  }
}
```

### 1.2 采购订单查询API
```
GET /api/purchase/list
参数：
  orderNo: 采购订单号
  supplierName: 供应商名称
  materialCode: 物资编码
  category: 大类
  userUnit: 用户单位
  startDate: 开始日期
  endDate: 结束日期
  page: 页码
  size: 每页记录数
响应：
{
  "success": true,
  "data": {
    "total": 1500,
    "pages": 150,
    "current": 1,
    "records": [
      {
        "id": 1,
        "orderNo": "PO20230615001",
        "planNumber": "PLAN001",
        "userUnit": "生产部",
        "category": "原材料",
        "orderDate": "2023-06-15",
        "supplierName": "供应商A",
        "materialGroup": "钢材",
        "totalAmount": 10000.00,
        "status": "PENDING",
        "items": [
          {
            "id": 1,
            "lineItemNumber": "10",
            "materialCode": "M001",
            "materialDescription": "钢板",
            "unit": "吨",
            "requestedQuantity": 10,
            "contractPrice": 1000.00,
            "contractAmount": 10000.00
          }
        ]
      }
    ]
  }
}
```

### 1.3 采购订单详情API
```
GET /api/purchase/{id}
响应：
{
  "success": true,
  "data": {
    "id": 1,
    "orderNo": "PO20230615001",
    "planNumber": "PLAN001",
    "userUnit": "生产部",
    "category": "原材料",
    "orderDate": "2023-06-15",
    "supplierName": "供应商A",
    "supplierCode": "S001",
    "materialGroup": "钢材",
    "factory": "上海工厂",
    "deliveryType": "WAREHOUSE",
    "totalAmount": 10000.00,
    "status": "PENDING",
    "createTime": "2023-06-15 10:00:00",
    "updateTime": "2023-06-15 10:00:00",
    "items": [
      {
        "id": 1,
        "lineItemNumber": "10",
        "materialCode": "M001",
        "materialDescription": "钢板",
        "unit": "吨",
        "requestedQuantity": 10,
        "contractPrice": 1000.00,
        "productStandard": "GB/T 700-2006",
        "contractAmount": 10000.00,
        "longDescription": "Q235B热轧钢板，厚度10mm",
        "priceFlag": "固定价",
        "purchaseOrderQuantity": 10
      }
    ]
  }
}
```

## 2. 工作流API

### 2.1 发起工作流API
```
POST /api/workflow/start
请求：
{
  "orderNo": "PO20230615001",
  "workflowType": "PURCHASE_CONFIRMATION",
  "deliveryType": "WAREHOUSE"
}
响应：
{
  "success": true,
  "data": {
    "workflowInstanceId": 1,
    "processInstanceId": "7601",
    "status": "RUNNING",
    "tasks": [
      {
        "id": 1,
        "taskName": "保管员确认",
        "assignee": {
          "id": 101,
          "name": "张三"
        },
        "status": "PENDING",
        "createTime": "2023-06-15 10:30:00"
      },
      {
        "id": 2,
        "taskName": "质检员确认",
        "assignee": {
          "id": 102,
          "name": "李四"
        },
        "status": "PENDING",
        "createTime": "2023-06-15 10:30:00"
      }
    ]
  }
}
```

### 2.2 任务处理API
```
POST /api/workflow/task/{taskId}/complete
请求：
{
  "approved": true,
  "comment": "物资已确认",
  "attachments": [
    {
      "name": "照片1.jpg",
      "content": "base64编码的文件内容"
    }
  ]
}
响应：
{
  "success": true,
  "data": {
    "taskId": 1,
    "status": "COMPLETED",
    "completeTime": "2023-06-15 11:00:00",
    "nextTasks": []
  }
}
```

### 2.3 待办任务查询API
```
GET /api/workflow/tasks/todo
参数：
  workflowType: 工作流类型
  page: 页码
  size: 每页记录数
响应：
{
  "success": true,
  "data": {
    "total": 50,
    "pages": 5,
    "current": 1,
    "records": [
      {
        "id": 1,
        "taskId": "7601",
        "taskName": "保管员确认",
        "workflowInstanceId": 1,
        "businessKey": "PO20230615001",
        "createTime": "2023-06-15 10:30:00",
        "dueDate": "2023-06-16 10:30:00",
        "priority": "NORMAL",
        "orderInfo": {
          "orderNo": "PO20230615001",
          "supplierName": "供应商A",
          "category": "原材料",
          "userUnit": "生产部"
        }
      }
    ]
  }
}
```

## 3. 确认单管理API

### 3.1 生成确认单API
```
POST /api/confirmation/generate
请求：
{
  "orderNo": "PO20230615001"
}
响应：
{
  "success": true,
  "data": {
    "confirmationId": 1,
    "confirmationNo": "CF20230615001",
    "orderNo": "PO20230615001",
    "status": "GENERATED",
    "pdfUrl": "/api/confirmation/1/pdf"
  }
}
```

### 3.2 确认单打印API
```
POST /api/confirmation/{id}/print
响应：
{
  "success": true,
  "data": {
    "confirmationId": 1,
    "printTime": "2023-06-15 15:00:00",
    "printBy": "王五",
    "status": "PRINTED"
  }
}
```

### 3.3 确认单查询API
```
GET /api/confirmation/list
参数：
  orderNo: 采购订单号
  confirmationNo: 确认单号
  status: 状态
  startDate: 开始日期
  endDate: 结束日期
  page: 页码
  size: 每页记录数
响应：
{
  "success": true,
  "data": {
    "total": 100,
    "pages": 10,
    "current": 1,
    "records": [
      {
        "id": 1,
        "confirmationNo": "CF20230615001",
        "orderNo": "PO20230615001",
        "supplierName": "供应商A",
        "category": "原材料",
        "userUnit": "生产部",
        "status": "PRINTED",
        "keeper": "张三",
        "inspector": "李四",
        "createTime": "2023-06-15 14:30:00",
        "printTime": "2023-06-15 15:00:00"
      }
    ]
  }
}
```

## 4. 数据看板API

### 4.1 领导层看板数据API
```
GET /api/dashboard/leadership
参数：
  timeRange: 时间范围(TODAY, WEEK, MONTH)
响应：
{
  "success": true,
  "data": {
    "orderCount": 150,
    "orderAmount": 1500000.00,
    "pendingWorkflowCount": 30,
    "qualityPassRate": 0.95,
    "inventoryValue": 5000000.00,
    "orderTrend": [
      {
        "date": "2023-06-01",
        "count": 10,
        "amount": 100000.00
      },
      // ...更多数据点
    ],
    "categoryDistribution": [
      {
        "category": "原材料",
        "count": 50,
        "amount": 500000.00,
        "percentage": 0.33
      },
      // ...更多分类
    ],
    "userUnitDistribution": [
      {
        "userUnit": "生产部",
        "count": 70,
        "amount": 700000.00,
        "percentage": 0.47
      },
      // ...更多用户单位
    ],
    "alerts": [
      {
        "type": "WORKFLOW_TIMEOUT",
        "message": "5个工作流超过24小时未处理",
        "count": 5,
        "level": "WARNING"
      },
      // ...更多警报
    ]
  }
}
```

### 4.2 运营看板数据API
```
GET /api/dashboard/operation
响应：
{
  "success": true,
  "data": {
    "workflowStats": {
      "total": 200,
      "running": 30,
      "completed": 170,
      "avgProcessTime": 8.5,
      "byType": [
        {
          "type": "PURCHASE_CONFIRMATION",
          "count": 150,
          "avgTime": 8.0
        },
        {
          "type": "DIRECT_DELIVERY",
          "count": 50,
          "avgTime": 10.0
        }
      ]
    },
    "storageStats": {
      "locationUsage": 0.75,
      "inboundCount": 120,
      "outboundCount": 100,
      "turnoverRate": 0.8,
      "byCategory": [
        {
          "category": "原材料",
          "quantity": 1000,
          "value": 1000000.00
        },
        // ...更多分类
      ]
    },
    "qualityStats": {
      "inspectionCount": 180,
      "passCount": 171,
      "failCount": 9,
      "passRate": 0.95,
      "failReasons": [
        {
          "reason": "规格不符",
          "count": 5,
          "percentage": 0.56
        },
        // ...更多原因
      ]
    }
  }
}
```
