# 仓储工作流系统技术方案文档

## 1. 系统架构

### 1.1 技术栈
后端：
- Spring Boot 3.x
- MySQL 8.x
- MyBatis-Plus
- Flowable
- RabbitMQ
- Redis
- Spring Security + JWT

前端：
- Vue 3 + TypeScript
- Element Plus
- Vite
- Pinia
- Vue Router

### 1.2 系统模块
```ascii
├── warehouse-admin        // 系统管理模块
├── warehouse-auth        // 认证授权模块
├── warehouse-common      // 公共模块
├── warehouse-workflow    // 工作流模块
├── warehouse-storage     // 仓储管理模块
├── warehouse-message     // 消息服务模块
└── warehouse-web        // 前端应用
```

## 2. 数据库设计

### 2.1 采购确认单相关表
```sql
-- 采购确认单主表
CREATE TABLE wh_purchase_order (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(32) COMMENT '采购单号',
    supplier_id BIGINT COMMENT '供应商ID',
    total_amount DECIMAL(15,2) COMMENT '总金额',
    status VARCHAR(20) COMMENT '状态',
    create_time DATETIME,
    update_time DATETIME,
    create_by BIGINT,
    update_by BIGINT
);

-- 采购确认单明细表
CREATE TABLE wh_purchase_order_item (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT COMMENT '采购单ID',
    material_code VARCHAR(32) COMMENT '物料编码',
    quantity INT COMMENT '数量',
    unit_price DECIMAL(15,2) COMMENT '单价',
    amount DECIMAL(15,2) COMMENT '金额'
);
```

### 2.2 仓储管理相关表
```sql
-- 仓库表
CREATE TABLE wh_warehouse (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(32) COMMENT '仓库编码',
    name VARCHAR(100) COMMENT '仓库名称',
    status VARCHAR(20) COMMENT '状态'
);

-- 库位表
CREATE TABLE wh_location (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    warehouse_id BIGINT COMMENT '仓库ID',
    code VARCHAR(32) COMMENT '库位编码',
    status VARCHAR(20) COMMENT '状态'
);

-- 库存表
CREATE TABLE wh_inventory (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    material_code VARCHAR(32) COMMENT '物料编码',
    location_id BIGINT COMMENT '库位ID',
    quantity INT COMMENT '数量',
    update_time DATETIME
);
```

### 2.3 质检相关表
```sql
-- 质检记录表
CREATE TABLE wh_quality_check (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT COMMENT '采购单ID',
    status VARCHAR(20) COMMENT '状态',
    check_result VARCHAR(20) COMMENT '检查结果',
    notes TEXT COMMENT '备注',
    check_time DATETIME,
    checker_id BIGINT
);
```

## 3. 接口设计

### 3.1 采购确认单接口
```
POST /api/purchase/import    // Excel导入
GET  /api/purchase/list     // 列表查询
GET  /api/purchase/{id}     // 详情查询
POST /api/purchase/approve  // 审批
```

### 3.2 仓储管理接口
```
POST /api/storage/in       // 入库
POST /api/storage/out      // 出库
GET  /api/storage/inventory // 库存查询
```

### 3.3 工作流接口
```
POST /api/workflow/start   // 启动流程
POST /api/workflow/approve // 审批
GET  /api/workflow/task    // 待办任务
```

## 4. 消息队列设计

### 4.1 交换机和队列
```
Exchange: warehouse.topic
Queues:
- warehouse.purchase.import    // 采购单导入
- warehouse.workflow.notify    // 工作流通知
- warehouse.inventory.change   // 库存变更
```

### 4.2 消息格式
```json
{
    "type": "PURCHASE_IMPORT",
    "data": {
        "orderId": "123",
        "status": "SUCCESS"
    },
    "timestamp": 1628160000000
}
```

## 5. 工作流程设计

### 5.1 采购确认流程
```
开始 -> 部门经理审批 -> [金额判断] -> 
    金额<10万: 采购经理审批
    10万<=金额<50万: 财务审批 -> 采购经理审批
    金额>=50万: 总经理审批 -> 采购经理审批
-> 结束
```

### 5.2 质检流程
```
开始 -> 质检 -> [质检结果] ->
    合格: 入库
    不合格: 退货处理
-> 结束
```

## 6. 安全设计

### 6.1 认证授权
- JWT Token认证
- 基于RBAC的权限控制
- 密码加密存储(BCrypt)

### 6.2 数据安全
- 操作日志记录
- 数据变更追踪
- SQL注入防护
- XSS防护

## 7. 部署方案

### 7.1 环境要求
- JDK 17+
- MySQL 8.x
- Redis 6.x
- RabbitMQ 3.x
- Nginx 1.20+

### 7.2 部署架构
```ascii
Client -> Nginx -> Spring Boot Applications -> 
    MySQL
    Redis
    RabbitMQ
```

## 8. 开发计划

### 8.1 第一阶段（5天）：基础框架
- Day 1: 项目初始化，数据库设计
- Day 2: 整合框架组件
- Day 3: 权限系统开发
- Day 4: 工作流引擎集成
- Day 5: 消息队列集成

### 8.2 第二阶段（15天）：核心功能
- Week 1: 采购确认单管理
- Week 2: 工作流功能实现
- Week 3: 仓储基础功能

### 8.3 第三阶段（20天）：业务功能
- Week 4-5: 仓储管理完善
- Week 6: 质检管理
- Week 7: 系统优化和测试