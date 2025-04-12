<template>
  <div class="confirmation-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>确认单列表</span>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="订单号">
          <el-input v-model="searchForm.order_no" placeholder="请输入订单号" clearable />
        </el-form-item>

        <el-form-item label="确认单号">
          <el-input v-model="searchForm.confirmation_no" placeholder="请输入确认单号" clearable />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="已生成" value="GENERATED" />
            <el-option label="已打印" value="PRINTED" />
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
        :data="confirmations"
        style="width: 100%"
        border
      >
        <el-table-column prop="confirmationNo" label="确认单号" width="180" />
        <el-table-column prop="orderNo" label="订单号" width="180" />
        <el-table-column prop="supplierName" label="供应商" width="180" />
        <el-table-column prop="category" label="大类" width="120" />
        <el-table-column prop="userUnit" label="用户单位" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="keeper" label="保管员" width="120" />
        <el-table-column prop="inspector" label="质检员" width="120" />
        <el-table-column prop="createTime" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDateDisplay(scope.row.createTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="printTime" label="打印时间" width="180">
          <template #default="scope">
            {{ formatDateDisplay(scope.row.printTime) }}
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="200">
          <template #default="scope">
            <el-button type="text" @click="viewConfirmation(scope.row)">查看</el-button>
            <el-button
              type="text"
              @click="printConfirmation(scope.row)"
              :disabled="scope.row.status !== 'GENERATED'"
            >
              打印
            </el-button>
            <el-button type="text" @click="downloadPdf(scope.row)">下载PDF</el-button>
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
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'ConfirmationList',

  setup() {
    const store = useStore()
    const router = useRouter()

    // 加载状态
    const loading = computed(() => store.getters.isLoading)

    // 分页参数
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = computed(() => store.getters['confirmation/total'])

    // 确认单数据
    const confirmations = computed(() => store.getters['confirmation/confirmations'])

    // 搜索表单
    const searchForm = reactive({
      order_no: '',
      confirmation_no: '',
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

    // 获取确认单列表
    const fetchConfirmations = async () => {
      try {
        await store.dispatch('confirmation/getConfirmations', {
          page: currentPage.value,
          size: pageSize.value,
          filters: searchForm
        })
      } catch (error) {
        console.error('获取确认单列表失败:', error)
        ElMessage.error(error.message || '获取确认单列表失败')
      }
    }

    // 搜索
    const handleSearch = () => {
      currentPage.value = 1
      fetchConfirmations()
    }

    // 重置搜索
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      dateRange.value = []
      currentPage.value = 1
      fetchConfirmations()
    }

    // 处理页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchConfirmations()
    }

    // 处理每页数量变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchConfirmations()
    }

    // 查看确认单详情
    const viewConfirmation = (confirmation) => {
      router.push(`/confirmation/${confirmation.id}`)
    }

    // 打印确认单
    const printConfirmation = async (confirmation) => {
      try {
        await store.dispatch('confirmation/printConfirmation', confirmation.id)
        ElMessage.success('确认单打印成功')
        fetchConfirmations()
      } catch (error) {
        console.error('打印确认单失败:', error)
        ElMessage.error(error.message || '打印确认单失败')
      }
    }

    // 下载PDF
    const downloadPdf = async (confirmation) => {
      try {
        const response = await store.dispatch('confirmation/getConfirmationPdf', confirmation.id)
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

    // 格式化日期显示
    const formatDateDisplay = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleString()
    }

    // 组件挂载时获取数据
    onMounted(() => {
      fetchConfirmations()
    })

    return {
      loading,
      currentPage,
      pageSize,
      total,
      confirmations,
      searchForm,
      dateRange,
      handleSearch,
      resetSearch,
      handleCurrentChange,
      handleSizeChange,
      viewConfirmation,
      printConfirmation,
      downloadPdf,
      getStatusType,
      getStatusText,
      formatDate,
      formatDateDisplay
    }
  }
}
</script>

<style scoped>
.confirmation-list-container {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>
