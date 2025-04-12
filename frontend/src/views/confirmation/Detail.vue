<template>
  <div class="confirmation-detail-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>确认单详情</span>
          <div class="header-actions">
            <el-button @click="$router.push('/confirmation')">返回列表</el-button>
            <el-button 
              type="primary" 
              @click="printConfirmation" 
              :disabled="!canPrint"
            >
              打印确认单
            </el-button>
            <el-button type="success" @click="downloadPdf">下载PDF</el-button>
          </div>
        </div>
      </template>
      
      <div v-if="confirmation">
        <!-- 确认单信息 -->
        <div class="confirmation-header">
          <h2>交付确认单</h2>
          <div class="confirmation-no">确认单号: {{ confirmation.confirmation_no }}</div>
        </div>
        
        <el-divider />
        
        <!-- 基本信息 -->
        <h3>基本信息</h3>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ order.supplier_name }}</el-descriptions-item>
          <el-descriptions-item label="供应商代码">{{ order.supplier_code || '-' }}</el-descriptions-item>
          <el-descriptions-item label="大类">{{ order.category }}</el-descriptions-item>
          <el-descriptions-item label="用户单位">{{ order.user_unit }}</el-descriptions-item>
          <el-descriptions-item label="订单日期">{{ formatDate(order.order_date) }}</el-descriptions-item>
          <el-descriptions-item label="交付类型">
            <el-tag :type="order.delivery_type === 'DIRECT' ? 'success' : 'primary'">
              {{ order.delivery_type === 'DIRECT' ? '直达' : '入库' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(confirmation.status)">
              {{ getStatusText(confirmation.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(confirmation.create_time) }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- 确认信息 -->
        <h3>确认信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="保管员">{{ confirmation.keeper ? confirmation.keeper.full_name : '-' }}</el-descriptions-item>
          <el-descriptions-item label="保管员确认时间">{{ formatDate(confirmation.keeper_confirm_time) }}</el-descriptions-item>
          <el-descriptions-item label="质检员">{{ confirmation.inspector ? confirmation.inspector.full_name : '-' }}</el-descriptions-item>
          <el-descriptions-item label="质检员确认时间">{{ formatDate(confirmation.inspector_confirm_time) }}</el-descriptions-item>
          <el-descriptions-item label="打印人">{{ confirmation.printer ? confirmation.printer.full_name : '-' }}</el-descriptions-item>
          <el-descriptions-item label="打印时间">{{ formatDate(confirmation.print_time) }}</el-descriptions-item>
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
        </el-table>
        
        <!-- 签名区域 -->
        <div class="signature-area">
          <div class="signature-item">
            <div class="signature-title">保管员签名</div>
            <div class="signature-line"></div>
            <div class="signature-date">日期: {{ formatDateShort(confirmation.keeper_confirm_time) }}</div>
          </div>
          
          <div class="signature-item">
            <div class="signature-title">质检员签名</div>
            <div class="signature-line"></div>
            <div class="signature-date">日期: {{ formatDateShort(confirmation.inspector_confirm_time) }}</div>
          </div>
          
          <div class="signature-item">
            <div class="signature-title">用户单位签名</div>
            <div class="signature-line"></div>
            <div class="signature-date">日期: </div>
          </div>
        </div>
      </div>
      
      <div v-else-if="!loading" class="empty-data">
        未找到确认单信息
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'ConfirmationDetail',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    // 加载状态
    const loading = computed(() => store.getters.isLoading)
    
    // 确认单数据
    const confirmation = ref(null)
    const order = ref({
      items: []
    })
    
    // 判断是否可以打印
    const canPrint = computed(() => {
      return confirmation.value && confirmation.value.status === 'GENERATED'
    })
    
    // 获取确认单详情
    const fetchConfirmationDetail = async () => {
      try {
        const id = route.params.id
        if (id) {
          // 这里假设有一个获取确认单详情的API
          // 实际实现可能需要根据后端API调整
          const response = await fetch(`/api/confirmation/${id}`)
          const data = await response.json()
          confirmation.value = data
          
          // 获取关联的订单信息
          if (confirmation.value && confirmation.value.order_id) {
            const orderResponse = await store.dispatch('purchase/getOrderById', confirmation.value.order_id)
            order.value = orderResponse
          }
        }
      } catch (error) {
        console.error('获取确认单详情失败:', error)
        ElMessage.error(error.message || '获取确认单详情失败')
      }
    }
    
    // 打印确认单
    const printConfirmation = async () => {
      try {
        if (!confirmation.value) return
        
        await store.dispatch('confirmation/printConfirmation', confirmation.value.id)
        ElMessage.success('确认单打印成功')
        fetchConfirmationDetail()
      } catch (error) {
        console.error('打印确认单失败:', error)
        ElMessage.error(error.message || '打印确认单失败')
      }
    }
    
    // 下载PDF
    const downloadPdf = async () => {
      try {
        if (!confirmation.value) return
        
        const response = await store.dispatch('confirmation/getConfirmationPdf', confirmation.value.id)
        if (response.success && response.data.url) {
          window.open(response.data.url, '_blank')
        } else {
          ElMessage.error('获取PDF失败')
        }
      } catch (error) {
        console.error('获取PDF失败:', error)
        ElMessage.error(error.message || '获取PDF失败')
      }
    }
    
    // 获取状态类型
    const getStatusType = (status) => {
      switch (status) {
        case 'GENERATED': return 'info'
        case 'PRINTED': return 'success'
        case 'COMPLETED': return 'success'
        case 'CANCELLED': return 'danger'
        default: return 'info'
      }
    }
    
    // 获取状态文本
    const getStatusText = (status) => {
      switch (status) {
        case 'GENERATED': return '已生成'
        case 'PRINTED': return '已打印'
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
    
    // 格式化短日期
    const formatDateShort = (date) => {
      if (!date) return '____________'
      return new Date(date).toLocaleDateString()
    }
    
    // 格式化货币
    const formatCurrency = (value) => {
      if (!value) return '¥0.00'
      return '¥' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
    }
    
    // 组件挂载时获取数据
    onMounted(() => {
      fetchConfirmationDetail()
    })
    
    return {
      loading,
      confirmation,
      order,
      canPrint,
      printConfirmation,
      downloadPdf,
      getStatusType,
      getStatusText,
      formatDate,
      formatDateShort,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.confirmation-detail-container {
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

.confirmation-header {
  text-align: center;
  margin-bottom: 20px;
}

.confirmation-header h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.confirmation-no {
  font-size: 16px;
  color: #606266;
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

.signature-area {
  display: flex;
  justify-content: space-between;
  margin-top: 50px;
  padding: 0 50px;
}

.signature-item {
  width: 200px;
  text-align: center;
}

.signature-title {
  margin-bottom: 50px;
  font-weight: bold;
}

.signature-line {
  border-bottom: 1px solid #000;
  margin-bottom: 10px;
}

.signature-date {
  text-align: left;
}
</style>
