<template>
  <div class="audit-list-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>出库单删除记录</span>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="物料凭证">
          <el-input
            v-model="searchForm.material_voucher"
            placeholder="请输入物料凭证"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="用料单位">
          <el-input
            v-model="searchForm.user_unit"
            placeholder="请输入用料单位"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待处理" value="PENDING" />
            <el-option label="已完成" value="COMPLETED" />
          </el-select>
        </el-form-item>
        <el-form-item label="删除日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            :shortcuts="dateShortcuts"
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
        :data="auditRecords"
        style="width: 100%"
        border
        :header-cell-style="{fontSize: '14px', fontWeight: 'bold'}"
        :cell-style="{fontSize: '13px'}"
        :row-style="{height: '40px'}"
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="material_voucher" label="物料凭证" min-width="100" />
        <el-table-column prop="voucher_date" label="开单日期" width="100">
          <template #default="scope">
            {{ formatDateDisplay(scope.row.voucher_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" min-width="100" />
        <el-table-column prop="user_unit" label="用料单位" min-width="100" />
        <el-table-column prop="status" label="删除时状态" width="90">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="delete_time" label="删除时间" width="150">
          <template #default="scope">
            {{ formatDateTime(scope.row.delete_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="delete_reason" label="删除原因" min-width="120" />
        <el-table-column prop="operator" label="操作人" width="80" />
        <el-table-column prop="items_count" label="物料数量" width="80" />
        <el-table-column fixed="right" label="操作" width="80">
          <template #default="scope">
            <div class="operation-buttons">
              <el-button type="primary" size="small" plain @click="viewAuditRecord(scope.row)">查看</el-button>
            </div>
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
          :page-sizes="[10, 20, 50, 100]"
          :current-page="currentPage"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

export default {
  name: 'AuditList',
  setup() {
    const store = useStore()
    const router = useRouter()
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(10)

    // 搜索表单
    const searchForm = reactive({
      material_voucher: '',
      user_unit: '',
      status: '',
      start_date: '',
      end_date: ''
    })

    // 日期范围
    const dateRange = ref([])
    const dateShortcuts = [
      {
        text: '最近一周',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
          return [start, end]
        }
      },
      {
        text: '最近一个月',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
          return [start, end]
        }
      },
      {
        text: '最近三个月',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
          return [start, end]
        }
      }
    ]

    // 监听日期范围变化
    watch(dateRange, (newVal) => {
      if (newVal && newVal.length === 2) {
        searchForm.start_date = newVal[0]
        searchForm.end_date = newVal[1]
      } else {
        searchForm.start_date = ''
        searchForm.end_date = ''
      }
    })

    // 获取审计记录
    const fetchAuditRecords = async () => {
      loading.value = true
      try {
        await store.dispatch('outbound/getAuditRecords', {
          page: currentPage.value,
          size: pageSize.value,
          filters: {
            material_voucher: searchForm.material_voucher,
            user_unit: searchForm.user_unit,
            status: searchForm.status,
            start_date: searchForm.start_date,
            end_date: searchForm.end_date
          }
        })
      } catch (error) {
        console.error('获取审计记录失败:', error)
        ElMessage.error('获取审计记录失败')
      } finally {
        loading.value = false
      }
    }

    // 审计记录数据
    const auditRecords = computed(() => {
      return store.getters['outbound/auditRecords'] || []
    })

    // 总记录数
    const total = computed(() => {
      return store.getters['outbound/auditTotal'] || 0
    })

    // 搜索
    const handleSearch = () => {
      currentPage.value = 1
      fetchAuditRecords()
    }

    // 重置搜索
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      dateRange.value = []
      currentPage.value = 1
      fetchAuditRecords()
    }

    // 分页
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchAuditRecords()
    }

    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchAuditRecords()
    }

    // 查看审计记录详情
    const viewAuditRecord = (record) => {
      router.push(`/outbound/audit/detail/${record.id}`)
    }

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

    // 组件挂载时获取数据
    onMounted(() => {
      fetchAuditRecords()
    })

    return {
      loading,
      currentPage,
      pageSize,
      auditRecords,
      total,
      searchForm,
      dateRange,
      dateShortcuts,
      handleSearch,
      resetSearch,
      handleCurrentChange,
      handleSizeChange,
      viewAuditRecord,
      getStatusType,
      getStatusText,
      formatDateDisplay,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.audit-list-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 12px;
}

.pagination-container {
  margin-top: 12px;
  display: flex;
  justify-content: center;
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
</style>
