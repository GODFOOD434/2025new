<template>
  <div class="workflow-detail-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>工作流详情</span>
          <el-button @click="$router.push('/workflow/tasks')">返回任务列表</el-button>
        </div>
      </template>
      
      <div v-if="workflow">
        <!-- 工作流基本信息 -->
        <h3>工作流信息</h3>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="流程实例ID">{{ workflow.process_instance_id }}</el-descriptions-item>
          <el-descriptions-item label="业务键">{{ workflow.business_key }}</el-descriptions-item>
          <el-descriptions-item label="工作流类型">
            <el-tag>{{ getWorkflowTypeText(workflow.workflow_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(workflow.status)">
              {{ getStatusText(workflow.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发起人">{{ workflow.initiator ? workflow.initiator.full_name : '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(workflow.create_time) }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- 任务列表 -->
        <h3>任务列表</h3>
        <el-table :data="workflow.tasks" style="width: 100%" border>
          <el-table-column prop="task_name" label="任务名称" width="150" />
          <el-table-column prop="assignee.full_name" label="处理人" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getTaskStatusType(scope.row.status)">
                {{ getTaskStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.create_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="complete_time" label="完成时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.complete_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="result" label="处理结果" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.result" :type="scope.row.result === 'APPROVED' ? 'success' : 'danger'">
                {{ scope.row.result === 'APPROVED' ? '同意' : '拒绝' }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="comment" label="处理意见" min-width="200" />
          <el-table-column fixed="right" label="操作" width="120">
            <template #default="scope">
              <el-button 
                v-if="scope.row.status === 'PENDING' && isCurrentUserTask(scope.row)"
                type="primary" 
                size="small" 
                @click="handleTask(scope.row)"
              >
                处理
              </el-button>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 相关订单 -->
        <h3 v-if="workflow.purchase_order">相关订单</h3>
        <el-descriptions v-if="workflow.purchase_order" :column="3" border>
          <el-descriptions-item label="订单号">{{ workflow.purchase_order.order_no }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ workflow.purchase_order.supplier_name }}</el-descriptions-item>
          <el-descriptions-item label="大类">{{ workflow.purchase_order.category }}</el-descriptions-item>
          <el-descriptions-item label="用户单位">{{ workflow.purchase_order.user_unit }}</el-descriptions-item>
          <el-descriptions-item label="订单日期">{{ formatDate(workflow.purchase_order.order_date) }}</el-descriptions-item>
          <el-descriptions-item label="总金额">{{ formatCurrency(workflow.purchase_order.total_amount) }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="action-buttons">
          <el-button 
            v-if="workflow.purchase_order"
            type="primary" 
            @click="viewOrder(workflow.purchase_order.id)"
          >
            查看订单详情
          </el-button>
        </div>
      </div>
      
      <div v-else-if="!loading" class="empty-data">
        未找到工作流信息
      </div>
    </el-card>
    
    <!-- 任务处理对话框 -->
    <el-dialog
      v-model="taskDialogVisible"
      :title="currentTask ? `处理任务: ${currentTask.task_name}` : '处理任务'"
      width="600px"
    >
      <div v-if="currentTask" class="task-detail">
        <h3>任务信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">{{ currentTask.task_name }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentTask.create_time) }}</el-descriptions-item>
        </el-descriptions>
        
        <h3>处理结果</h3>
        <el-form :model="taskForm" label-width="100px">
          <el-form-item label="审批结果">
            <el-radio-group v-model="taskForm.approved">
              <el-radio :label="true">同意</el-radio>
              <el-radio :label="false">拒绝</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="处理意见">
            <el-input
              v-model="taskForm.comment"
              type="textarea"
              :rows="3"
              placeholder="请输入处理意见"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="taskDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="completeTask" :loading="submitting">
            提交
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'WorkflowDetail',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    // 加载状态
    const loading = computed(() => store.getters.isLoading)
    const submitting = ref(false)
    
    // 工作流数据
    const workflow = ref(null)
    
    // 当前用户
    const currentUser = computed(() => store.getters['auth/currentUser'])
    
    // 任务处理对话框
    const taskDialogVisible = ref(false)
    const currentTask = ref(null)
    const taskForm = reactive({
      approved: true,
      comment: ''
    })
    
    // 获取工作流详情
    const fetchWorkflowDetail = async () => {
      try {
        const id = route.params.id
        if (id) {
          // 这里假设有一个获取工作流详情的API
          // 实际实现可能需要根据后端API调整
          const response = await fetch(`/api/workflow/${id}`)
          const data = await response.json()
          workflow.value = data.data
        }
      } catch (error) {
        console.error('获取工作流详情失败:', error)
        ElMessage.error(error.message || '获取工作流详情失败')
      }
    }
    
    // 判断是否是当前用户的任务
    const isCurrentUserTask = (task) => {
      return currentUser.value && task.assignee_id === currentUser.value.id
    }
    
    // 处理任务
    const handleTask = (task) => {
      currentTask.value = task
      taskForm.approved = true
      taskForm.comment = ''
      taskDialogVisible.value = true
    }
    
    // 完成任务
    const completeTask = async () => {
      if (!currentTask.value) return
      
      try {
        submitting.value = true
        
        await store.dispatch('workflow/completeTask', {
          taskId: currentTask.value.task_id,
          data: {
            approved: taskForm.approved,
            comment: taskForm.comment
          }
        })
        
        ElMessage.success('任务处理成功')
        taskDialogVisible.value = false
        fetchWorkflowDetail()
      } catch (error) {
        console.error('任务处理失败:', error)
        ElMessage.error(error.message || '任务处理失败')
      } finally {
        submitting.value = false
      }
    }
    
    // 查看订单详情
    const viewOrder = (orderId) => {
      router.push(`/purchase/${orderId}`)
    }
    
    // 获取工作流类型文本
    const getWorkflowTypeText = (type) => {
      switch (type) {
        case 'PURCHASE_CONFIRMATION': return '采购订单确认'
        case 'QUALITY_INSPECTION': return '质检'
        case 'OUTBOUND': return '出库'
        default: return type
      }
    }
    
    // 获取状态类型
    const getStatusType = (status) => {
      switch (status) {
        case 'CREATED': return 'info'
        case 'RUNNING': return 'warning'
        case 'COMPLETED': return 'success'
        case 'CANCELLED': return 'danger'
        default: return 'info'
      }
    }
    
    // 获取状态文本
    const getStatusText = (status) => {
      switch (status) {
        case 'CREATED': return '已创建'
        case 'RUNNING': return '运行中'
        case 'COMPLETED': return '已完成'
        case 'CANCELLED': return '已取消'
        default: return '未知'
      }
    }
    
    // 获取任务状态类型
    const getTaskStatusType = (status) => {
      switch (status) {
        case 'PENDING': return 'warning'
        case 'PROCESSING': return 'info'
        case 'COMPLETED': return 'success'
        case 'CANCELLED': return 'danger'
        default: return 'info'
      }
    }
    
    // 获取任务状态文本
    const getTaskStatusText = (status) => {
      switch (status) {
        case 'PENDING': return '待处理'
        case 'PROCESSING': return '处理中'
        case 'COMPLETED': return '已完成'
        case 'CANCELLED': return '已取消'
        default: return '未知'
      }
    }
    
    // 格式化日期
    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleString()
    }
    
    // 格式化货币
    const formatCurrency = (value) => {
      if (!value) return '¥0.00'
      return '¥' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
    }
    
    // 组件挂载时获取数据
    onMounted(() => {
      fetchWorkflowDetail()
    })
    
    return {
      loading,
      submitting,
      workflow,
      currentUser,
      taskDialogVisible,
      currentTask,
      taskForm,
      isCurrentUserTask,
      handleTask,
      completeTask,
      viewOrder,
      getWorkflowTypeText,
      getStatusType,
      getStatusText,
      getTaskStatusType,
      getTaskStatusText,
      formatDate,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.workflow-detail-container {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h3 {
  margin: 20px 0 10px;
  font-size: 18px;
  color: #303133;
}

.empty-data {
  text-align: center;
  padding: 30px 0;
  color: #909399;
  font-size: 14px;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.task-detail h3 {
  margin: 20px 0 10px;
  font-size: 16px;
  color: #303133;
}

.task-detail h3:first-child {
  margin-top: 0;
}
</style>
