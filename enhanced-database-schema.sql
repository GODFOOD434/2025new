-- Enhanced Purchase Order Table
ALTER TABLE wh_purchase_order 
ADD COLUMN plan_number VARCHAR(32) COMMENT '计划编号',
ADD COLUMN user_unit VARCHAR(100) COMMENT '用户单位',
ADD COLUMN category VARCHAR(50) COMMENT '大类',
ADD COLUMN order_date DATE COMMENT '订单生成日期',
ADD COLUMN supplier_code VARCHAR(32) COMMENT '供应商代码',
ADD COLUMN material_group VARCHAR(50) COMMENT '物料组',
ADD COLUMN first_level_product VARCHAR(100) COMMENT '一级目录产品',
ADD COLUMN factory VARCHAR(100) COMMENT '工厂',
ADD COLUMN delivery_type VARCHAR(20) COMMENT '交付类型(直达/仓储)';

-- Enhanced Purchase Order Item Table
ALTER TABLE wh_purchase_order_item
ADD COLUMN line_item_number VARCHAR(32) COMMENT '行项目号',
ADD COLUMN material_description VARCHAR(255) COMMENT '物资描述',
ADD COLUMN unit VARCHAR(20) COMMENT '计量单位',
ADD COLUMN requested_quantity INT COMMENT '申请数量',
ADD COLUMN contract_price DECIMAL(15,2) COMMENT '签约单价',
ADD COLUMN product_standard VARCHAR(100) COMMENT '产品标准',
ADD COLUMN contract_amount DECIMAL(15,2) COMMENT '签约金额',
ADD COLUMN long_description TEXT COMMENT '长描述',
ADD COLUMN price_flag VARCHAR(20) COMMENT '价格标志',
ADD COLUMN purchase_order_quantity INT COMMENT '采购订单数';

-- Staff Assignment Table
CREATE TABLE wh_staff_assignment (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    staff_id BIGINT COMMENT '员工ID',
    role_type VARCHAR(20) COMMENT '角色类型(保管员/质检员)',
    category VARCHAR(50) COMMENT '负责大类',
    user_unit VARCHAR(100) COMMENT '负责用户单位',
    create_time DATETIME,
    update_time DATETIME
);

-- Workflow Instance Table
CREATE TABLE wh_workflow_instance (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    process_instance_id VARCHAR(64) COMMENT 'Flowable流程实例ID',
    business_key VARCHAR(64) COMMENT '业务键(采购单号)',
    workflow_type VARCHAR(32) COMMENT '工作流类型',
    status VARCHAR(20) COMMENT '状态',
    initiator_id BIGINT COMMENT '发起人ID',
    create_time DATETIME,
    update_time DATETIME
);

-- Workflow Task Table
CREATE TABLE wh_workflow_task (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    task_id VARCHAR(64) COMMENT 'Flowable任务ID',
    workflow_instance_id BIGINT COMMENT '工作流实例ID',
    task_name VARCHAR(100) COMMENT '任务名称',
    assignee_id BIGINT COMMENT '处理人ID',
    status VARCHAR(20) COMMENT '状态',
    create_time DATETIME,
    complete_time DATETIME
);

-- Delivery Confirmation Table
CREATE TABLE wh_delivery_confirmation (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT COMMENT '采购单ID',
    confirmation_no VARCHAR(32) COMMENT '确认单号',
    keeper_id BIGINT COMMENT '保管员ID',
    inspector_id BIGINT COMMENT '质检员ID',
    keeper_confirm_time DATETIME COMMENT '保管员确认时间',
    inspector_confirm_time DATETIME COMMENT '质检员确认时间',
    status VARCHAR(20) COMMENT '状态',
    print_time DATETIME COMMENT '打印时间',
    create_time DATETIME,
    update_time DATETIME
);
