<template>
  <div class="audit-detail-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>删除记录详情</span>
          <div class="header-actions">
            <el-button @click="$router.push('/outbound/audit/list')">返回列表</el-button>
          </div>
        </div>
      </template>

      <div v-loading="loading">
        <!-- 基本信息 -->
        <div class="section">
          <h3>基本信息</h3>
          <el-descriptions :column="3" border size="small" :label-style="{fontSize: '13px', fontWeight: 'bold'}" :content-style="{fontSize: '13px'}">
            <el-descriptions-item label="物料凭证">{{ auditRecord.material_voucher }}</el-descriptions-item>
            <el-descriptions-item label="开单日期">{{ formatDateDisplay(auditRecord.voucher_date) }}</el-descriptions-item>
            <el-descriptions-item label="部门">{{ auditRecord.department }}</el-descriptions-item>
            <el-descriptions-item label="用料单位">{{ auditRecord.user_unit }}</el-descriptions-item>
            <el-descriptions-item label="单据类型">{{ auditRecord.document_type }}</el-descriptions-item>
            <el-descriptions-item label="合计金额">{{ formatCurrency(auditRecord.total_amount) }}</el-descriptions-item>
            <el-descriptions-item label="删除时状态">
              <el-tag :type="getStatusType(auditRecord.status)">
                {{ getStatusText(auditRecord.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="删除时间">{{ formatDateTime(auditRecord.delete_time) }}</el-descriptions-item>
            <el-descriptions-item label="操作人">{{ auditRecord.operator }}</el-descriptions-item>
            <el-descriptions-item :span="3" label="删除原因">{{ auditRecord.delete_reason }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 物料项 -->
        <div class="section">
          <h3>物料项</h3>
          <el-table
            :data="auditRecord.items || []"
            style="width: 100%"
            border
            :header-cell-style="{fontSize: '14px', fontWeight: 'bold'}"
            :cell-style="{fontSize: '13px'}"
            :row-style="{height: '40px'}"
          >
            <el-table-column prop="material_code" label="物料编码" min-width="100" />
            <el-table-column prop="material_description" label="物资名称及规格型号" min-width="150" />
            <el-table-column prop="unit" label="计量单位" width="80" />
            <el-table-column prop="requested_quantity" label="申请数量" width="80" />
            <el-table-column prop="actual_quantity" label="实拨数量" width="80" />
            <el-table-column prop="outbound_price" label="出库单价" width="90">
              <template #default="scope">
                {{ formatCurrency(scope.row.outbound_price) }}
              </template>
            </el-table-column>
            <el-table-column prop="outbound_amount" label="出库金额" width="90">
              <template #default="scope">
                {{ formatCurrency(scope.row.outbound_amount) }}
              </template>
            </el-table-column>
            <el-table-column prop="purchase_order_no" label="采购订单号" min-width="120" />
            <el-table-column prop="material_category_code" label="物料分类" min-width="100" />
            <el-table-column prop="project_code" label="项目编码" min-width="100" />
            <el-table-column prop="remark" label="备注" min-width="100" />
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

export default {
  name: 'AuditDetail',
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    const loading = ref(false)

    // 获取审计记录ID
    const auditId = computed(() => {
      return parseInt(route.params.id)
    })

    // 获取审计记录
    const fetchAuditRecord = async () => {
      if (!auditId.value) {
        ElMessage.error('无效的审计记录ID')
        router.push('/outbound/audit/list')
        return
      }

      loading.value = true
      try {
        await store.dispatch('outbound/getAuditRecord', auditId.value)
      } catch (error) {
        console.error('获取审计记录详情失败:', error)
        ElMessage.error('获取审计记录详情失败')
        router.push('/outbound/audit/list')
      } finally {
        loading.value = false
      }
    }

    // 审计记录数据
    const auditRecord = computed(() => {
      return store.getters['outbound/currentAuditRecord'] || {}
    })

    // 获取状态类型
    const getStatusType = (status) => {
      switch (status) {
        case 'PENDING':
          return 'warning'
        case 'COMPLETED':
          return 'success'
        default:
          return 'info'
      }
    }

    // 获取状态文本
    const getStatusText = (status) => {
      switch (status) {
        case 'PENDING':
          return '待处理'
        case 'COMPLETED':
          return '已完成'
        default:
          return '未知'
      }
    }

    // 格式化日期
    const formatDateDisplay = (dateStr) => {
      if (!dateStr) return ''
      return dayjs(dateStr).format('YYYY-MM-DD')
    }

    // 格式化日期时间
    const formatDateTime = (dateTimeStr) => {
      if (!dateTimeStr) return ''
      return dayjs(dateTimeStr).format('YYYY-MM-DD HH:mm:ss')
    }

    // 格式化货币
    const formatCurrency = (value) => {
      if (value === undefined || value === null) return ''
      return '¥ ' + parseFloat(value).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
    }

    // 组件挂载时获取数据
    onMounted(() => {
      fetchAuditRecord()
    })

    return {
      loading,
      auditRecord,
      getStatusType,
      getStatusText,
      formatDateDisplay,
      formatDateTime,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.audit-detail-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section {
  margin-bottom: 20px;
}

.section h3 {
  margin-bottom: 10px;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  border-left: 3px solid #409EFF;
  padding-left: 8px;
}
</style>
