<template>
  <div class="tasks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的任务</span>
          <el-radio-group v-model="workflowType" size="small" @change="handleTypeChange">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="PURCHASE_CONFIRMATION">采购订单确认</el-radio-button>
            <el-radio-button label="QUALITY_INSPECTION">质检</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <!-- 任务列表 -->
      <el-table
        v-loading="loading"
        :data="tasks"
        style="width: 100%"
        border
      >
        <el-table-column prop="taskName" label="任务名称" width="150" />
        <el-table-column prop="businessKey" label="业务单号" width="180" />
        <el-table-column label="订单信息" min-width="300">
          <template #default="scope">
            <div v-if="scope.row.orderInfo">
              <div>供应商: {{ scope.row.orderInfo.supplierName || '-' }}</div>
              <div>大类: {{ scope.row.orderInfo.category || '-' }}</div>
              <div>用户单位: {{ scope.row.orderInfo.userUnit || '-' }}</div>
            </div>
            <div v-else>-</div>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.createTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="dueDate" label="截止时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.dueDate) }}
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)">
              {{ getPriorityText(scope.row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="120">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleTask(scope.row)">
              处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
      
      <!-- 空数据 -->
      <el-empty v-if="tasks.length === 0 && !loading" description="暂无待办任务" />
    </el-card>
    
    <!-- 任务处理对话框 -->
    <el-dialog
      v-model="taskDialogVisible"
      :title="currentTask ? `处理任务: ${currentTask.taskName}` : '处理任务'"
      width="600px"
    >
      <div v-if="currentTask" class="task-detail">
        <h3>任务信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">{{ currentTask.taskName }}</el-descriptions-item>
          <el-descriptions-item label="业务单号">{{ currentTask.businessKey }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentTask.createTime) }}</el-descriptions-item>
          <el-descriptions-item label="截止时间">{{ formatDate(currentTask.dueDate) }}</el-descriptions-item>
        </el-descriptions>
        
        <h3>订单信息</h3>
        <el-descriptions v-if="currentTask.orderInfo" :column="2" border>
          <el-descriptions-item label="供应商">{{ currentTask.orderInfo.supplierName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="大类">{{ currentTask.orderInfo.category || '-' }}</el-descriptions-item>
          <el-descriptions-item label="用户单位">{{ currentTask.orderInfo.userUnit || '-' }}</el-descriptions-item>
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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'WorkflowTasks',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // 加载状态
    const loading = computed(() => store.getters.isLoading)
    const submitting = ref(false)
    
    // 分页参数
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = computed(() => store.getters['workflow/total'])
    
    // 任务数据
    const tasks = computed(() => store.getters['workflow/tasks'])
    
    // 工作流类型过滤
    const workflowType = ref('')
    
    // 任务处理对话框
    const taskDialogVisible = ref(false)
    const currentTask = ref(null)
    const taskForm = reactive({
      approved: true,
      comment: ''
    })
    
    // 获取任务列表
    const fetchTasks = async () => {
      try {
        const filters = {}
        if (workflowType.value) {
          filters.workflow_type = workflowType.value
        }
        
        await store.dispatch('workflow/getTasks', {
          page: currentPage.value,
          size: pageSize.value,
          filters
        })
      } catch (error) {
        console.error('获取任务列表失败:', error)
        ElMessage.error(error.message || '获取任务列表失败')
      }
    }
    
    // 处理工作流类型变化
    const handleTypeChange = () => {
      currentPage.value = 1
      fetchTasks()
    }
    
    // 处理页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchTasks()
    }
    
    // 处理每页数量变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchTasks()
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
          taskId: currentTask.value.taskId,
          data: {
            approved: taskForm.approved,
            comment: taskForm.comment
          }
        })
        
        ElMessage.success('任务处理成功')
        taskDialogVisible.value = false
        fetchTasks()
      } catch (error) {
        console.error('任务处理失败:', error)
        ElMessage.error(error.message || '任务处理失败')
      } finally {
        submitting.value = false
      }
    }
    
    // 获取优先级类型
    const getPriorityType = (priority) => {
      switch (priority) {
        case 'HIGH': return 'danger'
        case 'MEDIUM': return 'warning'
        case 'LOW': return 'info'
        default: return 'info'
      }
    }
    
    // 获取优先级文本
    const getPriorityText = (priority) => {
      switch (priority) {
        case 'HIGH': return '高'
        case 'MEDIUM': return '中'
        case 'LOW': return '低'
        default: return '普通'
      }
    }
    
    // 格式化日期
    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleString()
    }
    
    // 组件挂载时获取数据
    onMounted(() => {
      fetchTasks()
    })
    
    return {
      loading,
      submitting,
      currentPage,
      pageSize,
      total,
      tasks,
      workflowType,
      taskDialogVisible,
      currentTask,
      taskForm,
      handleTypeChange,
      handleCurrentChange,
      handleSizeChange,
      handleTask,
      completeTask,
      getPriorityType,
      getPriorityText,
      formatDate
    }
  }
}
</script>

<style scoped>
.tasks-container {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
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
