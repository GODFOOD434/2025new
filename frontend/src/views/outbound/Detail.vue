<template>
  <div class="outbound-detail-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>出库单详情</span>
          <div class="header-actions">
            <el-button @click="$router.push('/outbound')">返回列表</el-button>
            <el-button
              type="primary"
              @click="completeOutbound"
              :disabled="!canComplete"
            >
              完成出库
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="outbound">
        <!-- 基本信息 -->
        <h3>基本信息</h3>
        <el-descriptions :column="3" border size="default" :label-style="{fontSize: '13px', fontWeight: 'bold'}" :content-style="{fontSize: '13px'}">
          <el-descriptions-item label="物料凭证">{{ outbound.material_voucher }}</el-descriptions-item>
          <el-descriptions-item label="开单日期">{{ formatDate(outbound.voucher_date) }}</el-descriptions-item>
          <el-descriptions-item label="单据类型">{{ outbound.document_type || '正常出库' }}</el-descriptions-item>
          <el-descriptions-item label="具体用料部门">{{ outbound.department }}</el-descriptions-item>
          <el-descriptions-item label="用料单位">{{ outbound.user_unit }}</el-descriptions-item>
          <el-descriptions-item label="料单分属">{{ outbound.material_category || '-' }}</el-descriptions-item>
          <el-descriptions-item label="发料日期">{{ formatDate(outbound.issue_date) }}</el-descriptions-item>
          <el-descriptions-item label="转储订单/销售订单">{{ outbound.transfer_order || '-' }}</el-descriptions-item>
          <el-descriptions-item label="销售金额">{{ formatCurrency(outbound.sales_amount) }}</el-descriptions-item>
          <el-descriptions-item label="管理费率">{{ outbound.management_fee_rate ? `${outbound.management_fee_rate}%` : '-' }}</el-descriptions-item>
          <el-descriptions-item label="合计金额">{{ formatCurrency(outbound.total_amount) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(outbound.status)">
              {{ getStatusText(outbound.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="操作人">{{ outbound.operator ? outbound.operator.full_name : '-' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 出库项 -->
        <h3>出库项</h3>
        <el-table
          :data="outbound.items"
          style="width: 100%"
          border
          :header-cell-style="{fontSize: '14px', fontWeight: 'bold'}"
          :cell-style="{fontSize: '13px'}"
          :row-style="{height: '40px'}"
        >
          <el-table-column prop="material_code" label="物料编码" min-width="100" />
          <el-table-column prop="material_description" label="物资名称及规格型号" min-width="180" show-overflow-tooltip />
          <el-table-column prop="unit" label="计量单位" min-width="80" />
          <el-table-column prop="requested_quantity" label="应拨数量" min-width="80" />
          <el-table-column prop="actual_quantity" label="实拨数量" min-width="80" />
          <el-table-column prop="outbound_price" label="出库单价" min-width="90" align="right">
            <template #default="scope">
              {{ formatCurrency(scope.row.outbound_price) }}
            </template>
          </el-table-column>
          <el-table-column prop="outbound_amount" label="出库金额" min-width="90" align="right">
            <template #default="scope">
              {{ formatCurrency(scope.row.outbound_amount) }}
            </template>
          </el-table-column>
          <el-table-column prop="material_category_code" label="物资品种码" min-width="100" />
          <el-table-column prop="project_code" label="工程编码" min-width="100" />
          <el-table-column prop="purchase_order_no" label="采购订单号" min-width="120" />
          <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        </el-table>

        <!-- 库存信息 -->
        <h3>库存信息</h3>
        <el-table
          :data="inventoryData"
          style="width: 100%"
          border
          :header-cell-style="{fontSize: '14px', fontWeight: 'bold'}"
          :cell-style="{fontSize: '13px'}"
          :row-style="{height: '40px'}"
        >
          <el-table-column prop="material_code" label="物料编码" min-width="100" />
          <el-table-column prop="material_description" label="物资描述" min-width="180" show-overflow-tooltip />
          <el-table-column prop="current_quantity" label="当前库存" min-width="80" align="right" />
          <el-table-column prop="outbound_quantity" label="出库数量" min-width="80" align="right" />
          <el-table-column prop="remaining_quantity" label="剩余库存" min-width="80" align="right">
            <template #default="scope">
              <span :class="{ 'text-danger': scope.row.remaining_quantity < 0 }">
                {{ scope.row.remaining_quantity }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="库位" width="80" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.remaining_quantity < 0 ? 'danger' : 'success'">
                {{ scope.row.remaining_quantity < 0 ? '库存不足' : '库存充足' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else-if="!loading" class="empty-data">
        未找到出库单信息
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'OutboundDetail',

  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()

    // 加载状态
    const loading = computed(() => store.getters.isLoading)

    // 出库单数据
    const outbound = computed(() => store.getters['outbound/currentOutbound'])

    // 库存数据
    const inventoryData = ref([])

    // 判断是否可以完成出库
    const canComplete = computed(() => {
      return outbound.value && outbound.value.status === 'PENDING'
    })

    // 获取出库单详情
    const fetchOutboundDetail = async () => {
      try {
        const id = route.params.id
        if (id) {
          await store.dispatch('outbound/getOutboundById', id)

          // 获取相关库存信息
          if (outbound.value && outbound.value.items) {
            await fetchInventoryData()
          }
        }
      } catch (error) {
        console.error('获取出库单详情失败:', error)

        // 显示更详细的错误信息
        let errorMessage = '获取出库单详情失败'

        if (error.response) {
          // 服务器响应了但状态码不是2xx
          const status = error.response.status
          const data = error.response.data

          if (status === 404) {
            errorMessage = `出库单不存在 (ID: ${route.params.id})`
          } else if (status === 500) {
            errorMessage = `服务器错误: ${data?.detail || '未知错误'}`
          } else {
            errorMessage = `错误 (${status}): ${data?.detail || error.message || '未知错误'}`
          }

          console.error('API错误详情:', {
            status,
            data,
            url: error.config?.url
          })
        } else if (error.request) {
          // 请求发出但没有收到响应
          errorMessage = '服务器没有响应，请检查网络连接'

          // 检查是否是CORS错误
          if (error.message && error.message.includes('Network Error')) {
            errorMessage = 'CORS错误: 跨域请求被拒绝，请检查后端配置'
            console.error('CORS错误详情:', {
              message: error.message,
              url: error.config?.url
            })
          }
        }

        ElMessage.error(errorMessage)

        // 尝试重新连接
        setTimeout(() => {
          console.log('尝试重新获取出库单详情...')
          fetchOutboundDetail()
        }, 3000)
      }
    }

    // 获取库存数据
    const fetchInventoryData = async () => {
      // 首先初始化空数组，避免后续处理中出现undefined
      inventoryData.value = []

      if (!outbound.value || !outbound.value.items || outbound.value.items.length === 0) {
        console.log('没有出库项数据，不获取库存数据')
        return
      }

      try {
        // 收集有效的物料编码
        const materialCodes = outbound.value.items
          .map(item => item.material_code)
          .filter(code => code && code.trim && code.trim() !== '')

        if (materialCodes.length === 0) {
          console.log('没有有效的物料编码，不获取库存数据')
          initEmptyInventoryData()
          return
        }

        // 获取库存信息
        console.log('获取库存数据，物料编码:', materialCodes)
        try {
          const response = await store.dispatch('inventory/getInventories', {
            page: 1,
            size: 1000,
            filters: {
              material_codes: materialCodes.join(',')
            }
          })

          // 处理库存数据
          console.log('库存数据响应:', response)
          const inventories = (response && response.data && response.data.records) ? response.data.records : []

          // 合并出库项和库存数据
          inventoryData.value = outbound.value.items.map(item => {
            const inventory = inventories.find(inv => inv && inv.material_code === item.material_code) || {}
            return {
              material_code: item.material_code || '-',
              material_description: item.material_description || '-',
              current_quantity: inventory.quantity || 0,
              outbound_quantity: item.actual_quantity || 0,
              remaining_quantity: (inventory.quantity || 0) - (item.actual_quantity || 0),
              location: inventory.location || '-'
            }
          })

          console.log('合并后的库存数据:', inventoryData.value)
        } catch (apiError) {
          console.error('调用库存API失败:', apiError)
          initEmptyInventoryData()
        }
      } catch (error) {
        console.error('获取库存数据失败:', error)
        initEmptyInventoryData()
      }
    }

    // 初始化空库存数据的辅助函数
    const initEmptyInventoryData = () => {
      if (outbound.value && outbound.value.items) {
        inventoryData.value = outbound.value.items.map(item => ({
          material_code: item.material_code || '-',
          material_description: item.material_description || '-',
          current_quantity: 0,
          outbound_quantity: item.actual_quantity || 0,
          remaining_quantity: -(item.actual_quantity || 0),
          location: '-'
        }))
      } else {
        inventoryData.value = []
      }
      console.log('初始化空库存数据:', inventoryData.value)
    }

    // 完成出库
    const completeOutbound = () => {
      // 检查库存是否充足
      const insufficientItems = inventoryData.value.filter(item => item.remaining_quantity < 0)

      if (insufficientItems.length > 0) {
        ElMessageBox.confirm('存在库存不足的物料，是否继续完成出库操作？', '库存警告', {
          confirmButtonText: '继续',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          confirmCompleteOutbound()
        }).catch(() => {})
      } else {
        confirmCompleteOutbound()
      }
    }

    // 确认完成出库
    const confirmCompleteOutbound = () => {
      ElMessageBox.confirm('确定要完成此出库操作吗？此操作将更新库存数据。', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await store.dispatch('outbound/completeOutbound', outbound.value.id)
          ElMessage.success('出库操作已完成')
          fetchOutboundDetail()
        } catch (error) {
          console.error('完成出库失败:', error)
          ElMessage.error(error.message || '完成出库失败')
        }
      }).catch(() => {})
    }

    // 获取状态类型
    const getStatusType = (status) => {
      switch (status) {
        case 'PENDING': return 'info'
        case 'PROCESSING': return 'warning'
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
        case 'COMPLETED': return '已完成'
        case 'CANCELLED': return '已取消'
        default: return '未知'
      }
    }

    // 格式化日期
    const formatDate = (date) => {
      if (!date) return '-'

      try {
        // 尝试将日期转换为Date对象
        let dateObj;

        if (typeof date === 'string') {
          // 如果是字符串，直接转换
          dateObj = new Date(date);
        } else if (typeof date === 'number') {
          // 如果是数字，可能是Excel日期格式，使用特殊处理
          // Excel日期系统从1899-12-30开始计算，序列号1对应1900-01-01
          const baseDate = new Date(1899, 11, 30); // 1899-12-30
          const days = date;
          dateObj = new Date(baseDate.getTime() + days * 24 * 60 * 60 * 1000);
        } else {
          // 如果是其他类型，尝试直接转换
          dateObj = new Date(date);
        }

        // 检查日期是否有效
        if (isNaN(dateObj.getTime())) {
          console.warn('Invalid date:', date);
          return '-';
        }

        // 格式化日期为 YYYY-MM-DD
        const year = dateObj.getFullYear();
        const month = String(dateObj.getMonth() + 1).padStart(2, '0');
        const day = String(dateObj.getDate()).padStart(2, '0');

        return `${year}-${month}-${day}`;
      } catch (error) {
        console.error('Error formatting date:', error, date);
        return '-';
      }
    }

    // 格式化货币
    const formatCurrency = (value) => {
      if (!value) return '¥0.00'
      return '¥' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
    }

    // 组件挂载时获取数据
    onMounted(() => {
      fetchOutboundDetail()
    })

    return {
      loading,
      outbound,
      inventoryData,
      canComplete,
      completeOutbound,
      getStatusType,
      getStatusText,
      formatDate,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.outbound-detail-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  padding: 10px 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

h3 {
  margin: 15px 0 8px;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  padding: 4px 0;
  border-bottom: 1px solid #ebeef5;
}

.empty-data {
  text-align: center;
  padding: 30px 0;
  color: #909399;
  font-size: 14px;
}

.text-danger {
  color: #F56C6C;
  font-weight: bold;
}

/* 表格内容样式 */
.el-table {
  margin: 10px 0;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 描述列表样式 */
.el-descriptions {
  margin: 10px 0;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}
</style>
