<template>
  <div class="outbound-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>出库单列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="$router.push('/outbound/import')">导入出库单</el-button>
            <el-button type="danger" :disabled="selectedOutbounds.length === 0" @click="handleBatchDelete">批量删除</el-button>
            <el-button type="info" @click="$router.push('/outbound/audit/list')">查看删除记录</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="物料凭证">
          <el-input v-model="searchForm.material_voucher" placeholder="请输入物料凭证" clearable />
        </el-form-item>

        <el-form-item label="物料编码">
          <el-input v-model="searchForm.material_code" placeholder="请输入物料编码" clearable />
        </el-form-item>

        <el-form-item label="用料部门">
          <el-input v-model="searchForm.department" placeholder="请输入用料部门" clearable />
        </el-form-item>

        <el-form-item label="用料单位">
          <el-input v-model="searchForm.user_unit" placeholder="请输入用料单位" clearable />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待处理" value="PENDING" />
            <el-option label="处理中" value="PROCESSING" />
            <el-option label="已完成" value="COMPLETED" />
            <el-option label="已取消" value="CANCELLED" />
          </el-select>
        </el-form-item>

        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table
        v-loading="loading"
        :data="outbounds"
        style="width: 100%"
        border
        :header-cell-style="{fontSize: '15px', fontWeight: 'bold'}"
        :cell-style="{fontSize: '14px'}"
        :row-style="{height: '50px'}"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="35" align="center" />
        <el-table-column prop="material_voucher" label="物料凭证" min-width="120" />
        <el-table-column prop="voucher_date" label="开单日期" min-width="100">
          <template #default="scope">
            {{ formatDateDisplay(scope.row.voucher_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="department" label="用料部门" min-width="120" show-overflow-tooltip />
        <el-table-column prop="user_unit" label="用料单位" min-width="120" show-overflow-tooltip />
        <el-table-column prop="material_category" label="料单分属" min-width="100" />
        <el-table-column prop="document_type" label="单据类型" min-width="100" />
        <el-table-column label="采购订单号" min-width="120" show-overflow-tooltip>
          <template #default="scope">
            <template v-if="scope.row && hasPurchaseOrders(scope.row)">
              {{ getPurchaseOrders(scope.row) }}
            </template>
            <span v-else class="text-muted">无采购订单号</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="合计金额" min-width="100">
          <template #default="scope">
            {{ formatCurrency(scope.row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="80">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="large">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" min-width="120">
          <template #default="scope">
            {{ formatDateDisplay(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作人" min-width="80" />
        <el-table-column fixed="right" label="操作" width="220">
          <template #default="scope">
            <div class="operation-buttons">
              <el-button type="primary" size="small" plain @click="viewOutbound(scope.row)">查看</el-button>
              <el-button
                type="success"
                size="small"
                plain
                @click="completeOutbound(scope.row)"
                :disabled="scope.row.status !== 'PENDING'"
              >
                完成出库
              </el-button>
              <el-button
                type="danger"
                size="small"
                plain
                @click="handleDelete(scope.row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <div>
          <div class="debug-info" style="margin-bottom: 10px; padding: 8px; background-color: #f0f9eb; border-radius: 4px; border: 1px solid #e1f3d8;">
            <p style="margin: 0; font-size: 14px; color: #67c23a; font-weight: bold;">
              调试信息
            </p>
            <ul style="margin: 5px 0 0; padding-left: 20px; font-size: 14px; color: #606266;">
              <li>当前页: {{ currentPage }}</li>
              <li>每页数量: {{ pageSize }}</li>
              <li>总数: {{ total }}</li>
              <li>当前记录数: {{ outbounds.length }}</li>
            </ul>
          </div>
          <el-pagination
            background
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            :page-size="pageSize"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50, 100]"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            style="font-size: 14px; padding: 10px 0;"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'OutboundList',

  setup() {
    const store = useStore()
    const router = useRouter()

    // 加载状态
    const loading = computed(() => store.getters.isLoading)

    // 分页参数
    const currentPage = ref(1)
    const pageSize = ref(20) // 增加默认每页显示数量
    const total = computed(() => store.getters['outbound/total'])

    // 出库单数据
    const outbounds = computed(() => {
      const data = store.getters['outbound/outbounds']
      console.log('Outbounds data:', data)
      console.log('Outbounds count:', data ? data.length : 0)
      return data || [] // 确保返回数组，即使数据为 null
    })

    // 选中的出库单
    const selectedOutbounds = ref([])

    // 搜索表单
    const searchForm = reactive({
      material_voucher: '',
      material_code: '',
      department: '',
      user_unit: '',
      status: '',
      start_date: '',
      end_date: ''
    })

    // 日期范围
    const dateRange = ref([])

    // 监听日期范围变化
    watch(dateRange, (newVal) => {
      if (newVal && newVal.length === 2) {
        // 格式化日期为 YYYY-MM-DD 格式
        searchForm.start_date = formatDate(newVal[0])
        searchForm.end_date = formatDate(newVal[1])
      } else {
        searchForm.start_date = ''
        searchForm.end_date = ''
      }
    })

    // 格式化日期函数
    const formatDate = (date) => {
      if (!date) return ''

      // 如果是字符串，尝试转换为 Date 对象
      const d = typeof date === 'string' ? new Date(date) : date

      const year = d.getFullYear()
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')

      return `${year}-${month}-${day}`
    }

    // 获取出库单列表
    const fetchOutbounds = async () => {
      try {
        console.log('Fetching outbounds with params:', {
          page: currentPage.value,
          size: pageSize.value,
          filters: searchForm
        })

        await store.dispatch('outbound/getOutbounds', {
          page: currentPage.value,
          size: pageSize.value,
          filters: searchForm
        })

        console.log('Debug info after fetch:', {
          page: currentPage.value,
          size: pageSize.value,
          total: total.value,
          records: outbounds.value.length
        })
      } catch (error) {
        console.error('获取出库单列表失败:', error)
        ElMessage.error(error.message || '获取出库单列表失败')
      }
    }

    // 搜索
    const handleSearch = () => {
      currentPage.value = 1
      fetchOutbounds()
    }

    // 重置搜索
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      dateRange.value = []
      currentPage.value = 1
      fetchOutbounds()
    }

    // 处理页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchOutbounds()
    }

    // 处理每页数量变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchOutbounds()
    }

    // 查看出库单详情
    const viewOutbound = (outbound) => {
      router.push(`/outbound/${outbound.id}`)
    }

    // 检查是否有采购订单号
    const hasPurchaseOrders = (outbound) => {
      if (!outbound || !outbound.items) {
        return false
      }

      try {
        return Array.isArray(outbound.items) && outbound.items.some(item =>
          item && item.purchase_order_no && item.purchase_order_no.trim && item.purchase_order_no.trim() !== ''
        )
      } catch (error) {
        console.error('Error in hasPurchaseOrders:', error)
        return false
      }
    }

    // 获取采购订单号
    const getPurchaseOrders = (outbound) => {
      if (!outbound || !outbound.items || !Array.isArray(outbound.items) || outbound.items.length === 0) {
        return '无采购订单号'
      }

      try {
        // 收集所有不同的采购订单号
        const uniqueOrders = new Set()

        outbound.items.forEach(item => {
          if (item && item.purchase_order_no && typeof item.purchase_order_no === 'string' && item.purchase_order_no.trim() !== '') {
            uniqueOrders.add(item.purchase_order_no.trim())
          }
        })

        if (uniqueOrders.size === 0) {
          return '无采购订单号'
        }

        return Array.from(uniqueOrders).join(', ')
      } catch (error) {
        console.error('Error in getPurchaseOrders:', error)
        return '无采购订单号'
      }
    }

    // 完成出库
    const completeOutbound = (outbound) => {
      ElMessageBox.confirm('确定要完成此出库操作吗？此操作将更新库存数据。', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await store.dispatch('outbound/completeOutbound', outbound.id)
          ElMessage.success('出库操作已完成')
          fetchOutbounds()
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

    // 格式化日期显示
    const formatDateDisplay = (date) => {
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

    // 处理选择变化
    const handleSelectionChange = (selection) => {
      selectedOutbounds.value = selection
    }

    // 删除单个出库单
    const handleDelete = (outbound) => {
      // 创建删除原因输入框
      ElMessageBox.prompt(`请输入删除出库单 ${outbound.material_voucher} 的原因`, '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入删除原因',
        inputValidator: (value) => {
          if (outbound.status === 'COMPLETED' && !value) {
            return '已完成的出库单必须输入删除原因'
          }
          return true
        },
        type: 'warning'
      }).then(async ({ value: reason }) => {
        try {
          await store.dispatch('outbound/deleteOutbound', { id: outbound.id, reason })
          ElMessage.success('删除成功')
        } catch (error) {
          console.error('删除失败:', error)
          ElMessage.error(error.message || '删除失败')
        }
      }).catch(() => {})
    }

    // 批量删除
    const handleBatchDelete = () => {
      if (selectedOutbounds.value.length === 0) {
        ElMessage.warning('请选择要删除的出库单')
        return
      }

      // 检查是否有已完成的出库单
      const hasCompletedOrders = selectedOutbounds.value.some(item => item.status === 'COMPLETED')
      const promptMessage = hasCompletedOrders
        ? `选中的出库单中包含已完成的记录，请输入删除原因（必填）`
        : `请输入删除选中的 ${selectedOutbounds.value.length} 个出库单的原因（可选）`

      ElMessageBox.prompt(promptMessage, '批量删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入删除原因',
        inputValidator: (value) => {
          if (hasCompletedOrders && !value) {
            return '包含已完成的出库单时，必须输入删除原因'
          }
          return true
        },
        type: 'warning'
      }).then(async ({ value: reason }) => {
        try {
          const ids = selectedOutbounds.value.map(item => item.id)
          await store.dispatch('outbound/batchDeleteOutbounds', { ids, reason })
          ElMessage.success('批量删除成功')
          // 清空选中项
          selectedOutbounds.value = []
        } catch (error) {
          console.error('批量删除失败:', error)
          ElMessage.error(error.message || '批量删除失败')
        }
      }).catch(() => {})
    }

    // 组件挂载时获取数据
    onMounted(() => {
      fetchOutbounds()
    })

    return {
      loading,
      currentPage,
      pageSize,
      total,
      outbounds,
      searchForm,
      dateRange,
      selectedOutbounds,
      handleSearch,
      resetSearch,
      handleCurrentChange,
      handleSizeChange,
      viewOutbound,
      completeOutbound,
      getStatusType,
      getStatusText,
      formatDate,
      formatDateDisplay,
      formatCurrency,
      handleSelectionChange,
      handleDelete,
      handleBatchDelete,
      // 添加采购订单号相关方法
      hasPurchaseOrders,
      getPurchaseOrders
    }
  }
}
</script>

<style scoped>
.outbound-list-container {
  padding: 0;
}

.text-muted {
  color: #909399;
  font-style: italic;
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

.search-form {
  margin-bottom: 12px;
  font-size: 14px;
}

.search-form .el-form-item {
  margin-bottom: 10px;
}

.search-form .el-input {
  width: 180px;
}

.pagination-container {
  margin-top: 12px;
  text-align: right;
}

/* 表格内容样式 */
.el-table {
  margin: 10px 0;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 表格操作按钮样式 */
.operation-buttons {
  display: flex;
  justify-content: space-around;
  flex-wrap: nowrap;
  gap: 8px;
}

.operation-buttons .el-button {
  padding: 4px 10px;
  font-size: 13px;
  min-width: 60px;
}

.el-table .el-button + .el-button {
  margin-left: 0;
}
</style>
