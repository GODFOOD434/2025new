<template>
  <div class="order-detail-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>采购订单详情</span>
          <div class="header-actions">
            <el-button @click="$router.push('/purchase')">返回列表</el-button>
            <el-button 
              type="primary" 
              @click="startWorkflow" 
              :disabled="!canStartWorkflow"
            >
              发起工作流
            </el-button>
            <el-button 
              type="success" 
              @click="generateConfirmation" 
              :disabled="!canGenerateConfirmation"
            >
              生成确认单
            </el-button>
          </div>
        </div>
      </template>
      
      <div v-if="order">
        <!-- 基本信息 -->
        <h3>基本信息</h3>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
          <el-descriptions-item label="计划编号">{{ order.plan_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="订单日期">{{ formatDate(order.order_date) }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ order.supplier_name }}</el-descriptions-item>
          <el-descriptions-item label="供应商代码">{{ order.supplier_code || '-' }}</el-descriptions-item>
          <el-descriptions-item label="大类">{{ order.category }}</el-descriptions-item>
          <el-descriptions-item label="用户单位">{{ order.user_unit }}</el-descriptions-item>
          <el-descriptions-item label="物料组">{{ order.material_group || '-' }}</el-descriptions-item>
          <el-descriptions-item label="一级目录产品">{{ order.first_level_product || '-' }}</el-descriptions-item>
          <el-descriptions-item label="工厂">{{ order.factory || '-' }}</el-descriptions-item>
          <el-descriptions-item label="交付类型">
            <el-tag :type="order.delivery_type === 'DIRECT' ? 'success' : 'primary'">
              {{ order.delivery_type === 'DIRECT' ? '直达' : '入库' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(order.status)">
              {{ getStatusText(order.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总金额" :span="3">
            {{ formatCurrency(order.total_amount) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 订单项 -->
        <h3>订单项</h3>
        <el-table :data="order.items" style="width: 100%" border>
          <el-table-column prop="line_item_number" label="行项目号" width="100" />
          <el-table-column prop="material_code" label="物料编码" width="120" />
          <el-table-column prop="material_description" label="物资描述" min-width="200" />
          <el-table-column prop="unit" label="计量单位" width="80" />
          <el-table-column prop="requested_quantity" label="申请数量" width="100" />
          <el-table-column prop="contract_price" label="签约单价" width="100">
            <template #default="scope">
              {{ formatCurrency(scope.row.contract_price) }}
            </template>
          </el-table-column>
          <el-table-column prop="contract_amount" label="签约金额" width="120">
            <template #default="scope">
              {{ formatCurrency(scope.row.contract_amount) }}
            </template>
          </el-table-column>
          <el-table-column prop="product_standard" label="产品标准" width="120" />
        </el-table>
      </div>
      
      <div v-else-if="!loading" class="empty-data">
        未找到订单信息
      </div>
    </el-card>
    
    <!-- 工作流对话框 -->
    <el-dialog
      v-model="workflowDialogVisible"
      title="发起工作流"
      width="500px"
    >
      <el-form :model="workflowForm" label-width="100px">
        <el-form-item label="订单号">
          <el-input v-model="workflowForm.order_no" disabled />
        </el-form-item>
        
        <el-form-item label="工作流类型">
          <el-select v-model="workflowForm.workflow_type" placeholder="请选择工作流类型">
            <el-option label="采购订单确认" value="PURCHASE_CONFIRMATION" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="交付类型">
          <el-radio-group v-model="workflowForm.delivery_type">
            <el-radio label="DIRECT">直达</el-radio>
            <el-radio label="WAREHOUSE">入库</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="workflowDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmStartWorkflow" :loading="submitting">
            确认
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
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'OrderDetail',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    // 加载状态
    const loading = computed(() => store.getters.isLoading)
    const submitting = ref(false)
    
    // 订单数据
    const order = computed(() => store.getters['purchase/currentOrder'])
    
    // 工作流对话框
    const workflowDialogVisible = ref(false)
    const workflowForm = reactive({
      order_no: '',
      workflow_type: 'PURCHASE_CONFIRMATION',
      delivery_type: 'WAREHOUSE'
    })
    
    // 判断是否可以发起工作流
    const canStartWorkflow = computed(() => {
      return order.value && order.value.status === 'PENDING'
    })
    
    // 判断是否可以生成确认单
    const canGenerateConfirmation = computed(() => {
      return order.value && order.value.status === 'CONFIRMED'
    })
    
    // 获取订单详情
    const fetchOrderDetail = async () => {
      try {
        const id = route.params.id
        if (id) {
          await store.dispatch('purchase/getOrderById', id)
        }
      } catch (error) {
        console.error('获取订单详情失败:', error)
        ElMessage.error(error.message || '获取订单详情失败')
      }
    }
    
    // 发起工作流
    const startWorkflow = () => {
      if (!order.value) return
      
      workflowForm.order_no = order.value.order_no
      workflowForm.delivery_type = order.value.delivery_type
      workflowDialogVisible.value = true
    }
    
    // 确认发起工作流
    const confirmStartWorkflow = async () => {
      try {
        submitting.value = true
        await store.dispatch('workflow/startWorkflow', workflowForm)
        ElMessage.success('工作流发起成功')
        workflowDialogVisible.value = false
        fetchOrderDetail()
      } catch (error) {
        console.error('发起工作流失败:', error)
        ElMessage.error(error.message || '发起工作流失败')
      } finally {
        submitting.value = false
      }
    }
    
    // 生成确认单
    const generateConfirmation = async () => {
      if (!order.value) return
      
      try {
        ElMessageBox.confirm('确定要为该订单生成确认单吗?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(async () => {
          const response = await store.dispatch('confirmation/generateConfirmation', order.value.order_no)
          ElMessage.success('确认单生成成功')
          router.push(`/confirmation/${response.data.confirmationId}`)
        }).catch(() => {})
      } catch (error) {
        console.error('生成确认单失败:', error)
        ElMessage.error(error.message || '生成确认单失败')
      }
    }
    
    // 获取状态类型
    const getStatusType = (status) => {
      switch (status) {
        case 'PENDING': return 'info'
        case 'PROCESSING': return 'warning'
        case 'CONFIRMED': return 'success'
        case 'COMPLETED': return 'success'
        case 'CANCELLED': return 'danger'
        default: return 'info'
      }
    }
    
    // 获取状态文本
    const getStatusText = (status) => {
      switch (status) {
        case 'PENDING': return '待处理'
        case 'PROCESSING': return '处理中'
        case 'CONFIRMED': return '已确认'
        case 'COMPLETED': return '已完成'
        case 'CANCELLED': return '已取消'
        default: return '未知'
      }
    }
    
    // 格式化日期
    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleDateString()
    }
    
    // 格式化货币
    const formatCurrency = (value) => {
      if (!value) return '¥0.00'
      return '¥' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
    }
    
    // 组件挂载时获取数据
    onMounted(() => {
      fetchOrderDetail()
    })
    
    return {
      loading,
      submitting,
      order,
      workflowDialogVisible,
      workflowForm,
      canStartWorkflow,
      canGenerateConfirmation,
      startWorkflow,
      confirmStartWorkflow,
      generateConfirmation,
      getStatusType,
      getStatusText,
      formatDate,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.order-detail-container {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
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
</style>
