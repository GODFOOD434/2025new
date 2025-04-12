import unittest
from app.models.user import User, Role
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, DeliveryType, PurchaseOrderStatus
from app.models.workflow import WorkflowInstance, WorkflowTask, WorkflowType, WorkflowStatus, TaskStatus


class TestModels(unittest.TestCase):
    """测试模型类"""
    
    def test_user_model(self):
        """测试用户模型"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User",
            is_active=True,
            is_superuser=False
        )
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.hashed_password, "hashed_password")
        self.assertEqual(user.full_name, "Test User")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
    
    def test_role_model(self):
        """测试角色模型"""
        role = Role(
            name="admin",
            description="系统管理员"
        )
        
        self.assertEqual(role.name, "admin")
        self.assertEqual(role.description, "系统管理员")
    
    def test_purchase_order_model(self):
        """测试采购订单模型"""
        order = PurchaseOrder(
            order_no="PO20230615001",
            plan_number="PLAN001",
            user_unit="生产部",
            category="原材料",
            supplier_name="供应商A",
            delivery_type=DeliveryType.WAREHOUSE,
            status=PurchaseOrderStatus.PENDING
        )
        
        self.assertEqual(order.order_no, "PO20230615001")
        self.assertEqual(order.plan_number, "PLAN001")
        self.assertEqual(order.user_unit, "生产部")
        self.assertEqual(order.category, "原材料")
        self.assertEqual(order.supplier_name, "供应商A")
        self.assertEqual(order.delivery_type, DeliveryType.WAREHOUSE)
        self.assertEqual(order.status, PurchaseOrderStatus.PENDING)
    
    def test_workflow_instance_model(self):
        """测试工作流实例模型"""
        workflow = WorkflowInstance(
            process_instance_id="WF20230615001",
            business_key="PO20230615001",
            workflow_type=WorkflowType.PURCHASE_CONFIRMATION,
            status=WorkflowStatus.RUNNING
        )
        
        self.assertEqual(workflow.process_instance_id, "WF20230615001")
        self.assertEqual(workflow.business_key, "PO20230615001")
        self.assertEqual(workflow.workflow_type, WorkflowType.PURCHASE_CONFIRMATION)
        self.assertEqual(workflow.status, WorkflowStatus.RUNNING)
    
    def test_workflow_task_model(self):
        """测试工作流任务模型"""
        task = WorkflowTask(
            task_id="TASK20230615001",
            workflow_instance_id=1,
            task_name="保管员确认",
            status=TaskStatus.PENDING
        )
        
        self.assertEqual(task.task_id, "TASK20230615001")
        self.assertEqual(task.workflow_instance_id, 1)
        self.assertEqual(task.task_name, "保管员确认")
        self.assertEqual(task.status, TaskStatus.PENDING)


if __name__ == "__main__":
    unittest.main()
