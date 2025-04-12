<template>
  <div class="order-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>采购订单列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="$router.push('/purchase/import')">导入订单</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="订单号">
          <el-input v-model="searchForm.order_no" placeholder="请输入订单号" clearable />
        </el-form-item>

        <el-form-item label="供应商">
          <el-input v-model="searchForm.supplier_name" placeholder="请输入供应商名称" clearable />
        </el-form-item>

        <el-form-item label="物料编码">
          <el-input v-model="searchForm.material_code" placeholder="请输入物料编码" clearable />
        </el-form-item>

        <el-form-item label="大类">
          <el-select
            v-model="searchForm.category"
            placeholder="请选择"
            clearable
            filterable
            allow-create
            default-first-option
            :filter-method="filterCategory"
            style="width: 78px"
          >
            <el-option
              v-for="item in filteredCategoryOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="用户单位">
          <el-select
            v-model="searchForm.user_unit"
            placeholder="请选择"
            clearable
            filterable
            allow-create
            default-first-option
            style="width: 120px"
          >
            <el-option
              v-for="item in userUnitOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="订单日期">
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
        :data="orders"
        style="width: 100%"
        border
      >
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="supplier_name" label="供应商" width="180" />
        <el-table-column prop="category" label="大类" width="120" />
        <el-table-column prop="user_unit" label="用户单位" width="150" />
        <el-table-column prop="order_date" label="订单日期" width="120">
          <template #default="scope">
            {{ formatDate(scope.row.order_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额" width="120">
          <template #default="scope">
            {{ formatCurrency(scope.row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="delivery_type" label="交付类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.delivery_type === 'DIRECT' ? 'success' : 'primary'">
              {{ scope.row.delivery_type === 'DIRECT' ? '直达' : '入库' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="200">
          <template #default="scope">
            <el-button type="text" @click="viewOrder(scope.row)">查看</el-button>
            <el-button type="text" @click="startWorkflow(scope.row)" :disabled="!canStartWorkflow(scope.row)">
              发起工作流
            </el-button>
            <el-button type="text" @click="generateConfirmation(scope.row)" :disabled="!canGenerateConfirmation(scope.row)">
              生成确认单
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'OrderList',

  setup() {
    const store = useStore()
    const router = useRouter()

    // 加载状态
    const loading = computed(() => store.getters.isLoading)
    const submitting = ref(false)

    // 分页参数
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = computed(() => store.getters['purchase/total'])

    // 订单数据
    const orders = computed(() => store.getters['purchase/orders'])

    // 搜索表单
    const searchForm = reactive({
      order_no: '',
      supplier_name: '',
      material_code: '',
      category: '',
      user_unit: '',
      start_date: '',
      end_date: ''
    })

    // 日期范围
    const dateRange = ref([])

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

    // 大类选项 (01-61范围)
    const categoryOptions = ref([
      // 添加空选项作为默认值
      { value: '', label: '全部' },
      { value: '01', label: '01-原材料' },
      { value: '02', label: '02-半成品' },
      { value: '03', label: '03-成品' },
      { value: '04', label: '04-商品' },
      { value: '05', label: '05-外购件' },
      { value: '06', label: '06-外协件' },
      { value: '07', label: '07-外购工具' },
      { value: '08', label: '08-办公用品' },
      { value: '09', label: '09-低值易耗品' },
      { value: '10', label: '10-包装物' },
      { value: '11', label: '11-燃料' },
      { value: '12', label: '12-备件' },
      { value: '13', label: '13-修理用备件' },
      { value: '14', label: '14-辅助材料' },
      { value: '15', label: '15-建筑材料' },
      { value: '16', label: '16-化工原料' },
      { value: '17', label: '17-化工产品' },
      { value: '18', label: '18-化学试剂' },
      { value: '19', label: '19-油漆' },
      { value: '20', label: '20-润滑油' },
      { value: '21', label: '21-煤炭' },
      { value: '22', label: '22-其他物资' },
      { value: '23', label: '23-设备' },
      { value: '24', label: '24-仪器仪表' },
      { value: '25', label: '25-工具' },
      { value: '26', label: '26-模具' },
      { value: '27', label: '27-采样器具' },
      { value: '28', label: '28-量具' },
      { value: '29', label: '29-工装具' },
      { value: '30', label: '30-计算机软件' },
      { value: '31', label: '31-计算机硬件' },
      { value: '32', label: '32-通讯设备' },
      { value: '33', label: '33-办公设备' },
      { value: '34', label: '34-家具' },
      { value: '35', label: '35-家用电器' },
      { value: '36', label: '36-卫生材料' },
      { value: '37', label: '37-消防器材' },
      { value: '38', label: '38-安全防护用品' },
      { value: '39', label: '39-劳保用品' },
      { value: '40', label: '40-食品' },
      { value: '41', label: '41-饮料' },
      { value: '42', label: '42-烟酒' },
      { value: '43', label: '43-药品' },
      { value: '44', label: '44-医疗器械' },
      { value: '45', label: '45-医疗器具' },
      { value: '46', label: '46-卫生材料' },
      { value: '47', label: '47-消毒材料' },
      { value: '48', label: '48-消毒器具' },
      { value: '49', label: '49-消毒设备' },
      { value: '50', label: '50-消毒药品' },
      { value: '51', label: '51-消毒剂' },
      { value: '52', label: '52-消毒器械' },
      { value: '53', label: '53-消毒器具' },
      { value: '54', label: '54-消毒设备' },
      { value: '55', label: '55-消毒药品' },
      { value: '56', label: '56-消毒剂' },
      { value: '57', label: '57-消毒器械' },
      { value: '58', label: '58-消毒器具' },
      { value: '59', label: '59-消毒设备' },
      { value: '60', label: '60-消毒药品' },
      { value: '61', label: '61-消毒剂' }
    ])

    // 过滤后的大类选项
    const filteredCategoryOptions = ref(categoryOptions.value)

    // 过滤大类选项的方法
    const filterCategory = (query) => {
      if (query) {
        // 如果输入的是数字，则按编号过滤
        if (/^\d+$/.test(query)) {
          filteredCategoryOptions.value = categoryOptions.value.filter(item =>
            item.value.startsWith(query)
          )
        } else {
          // 否则按标签过滤
          filteredCategoryOptions.value = categoryOptions.value.filter(item =>
            item.label.toLowerCase().includes(query.toLowerCase())
          )
        }
      } else {
        // 如果没有输入，显示所有选项
        filteredCategoryOptions.value = categoryOptions.value
      }
    }

    // 用户单位选项
    const userUnitOptions = ref([])

    // 获取用户单位选项
    const fetchUserUnits = async () => {
      try {
        const response = await store.dispatch('purchase/getUserUnits')
        if (response && Array.isArray(response)) {
          // 将获取到的用户单位转换为选项格式
          userUnitOptions.value = response.map(unit => ({
            value: unit,
            label: unit
          }))
          // 添加空选项
          userUnitOptions.value.unshift({ value: '', label: '全部' })
        }
      } catch (error) {
        console.error('获取用户单位失败:', error)
        // 如果获取失败，使用默认选项
        userUnitOptions.value = [
          { value: '获取失败', label: '获取失败' },
        
        ]
      }
    }

    // 工作流对话框
    const workflowDialogVisible = ref(false)
    const workflowForm = reactive({
      order_no: '',
      workflow_type: 'PURCHASE_CONFIRMATION',
      delivery_type: 'WAREHOUSE'
    })

    // 获取订单列表
    const fetchOrders = async () => {
      try {
        await store.dispatch('purchase/getOrders', {
          page: currentPage.value,
          size: pageSize.value,
          filters: searchForm
        })
      } catch (error) {
        console.error('获取订单列表失败:', error)
      }
    }

    // 搜索
    const handleSearch = () => {
      currentPage.value = 1
      fetchOrders()
    }

    // 重置搜索
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      dateRange.value = []
      currentPage.value = 1
      fetchOrders()
    }

    // 处理页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchOrders()
    }

    // 处理每页数量变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchOrders()
    }

    // 查看订单详情
    const viewOrder = (order) => {
      router.push(`/purchase/${order.id}`)
    }

    // 发起工作流
    const startWorkflow = (order) => {
      workflowForm.order_no = order.order_no
      workflowForm.delivery_type = order.delivery_type
      workflowDialogVisible.value = true
    }

    // 确认发起工作流
    const confirmStartWorkflow = async () => {
      try {
        submitting.value = true
        await store.dispatch('workflow/startWorkflow', workflowForm)
        ElMessage.success('工作流发起成功')
        workflowDialogVisible.value = false
        fetchOrders()
      } catch (error) {
        console.error('发起工作流失败:', error)
        ElMessage.error(error.message || '发起工作流失败')
      } finally {
        submitting.value = false
      }
    }

    // 生成确认单
    const generateConfirmation = async (order) => {
      try {
        ElMessageBox.confirm('确定要为该订单生成确认单吗?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(async () => {
          const response = await store.dispatch('confirmation/generateConfirmation', order.order_no)
          ElMessage.success('确认单生成成功')
          router.push(`/confirmation/${response.data.confirmationId}`)
        }).catch(() => {})
      } catch (error) {
        console.error('生成确认单失败:', error)
        ElMessage.error(error.message || '生成确认单失败')
      }
    }

    // 判断是否可以发起工作流
    const canStartWorkflow = (order) => {
      return order.status === 'PENDING'
    }

    // 判断是否可以生成确认单
    const canGenerateConfirmation = (order) => {
      return order.status === 'CONFIRMED'
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
      if (!date) return ''
      return new Date(date).toLocaleDateString()
    }

    // 格式化货币
    const formatCurrency = (value) => {
      if (!value) return '¥0.00'
      return '¥' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
    }

    // 组件挂载时获取数据
    onMounted(() => {
      fetchOrders()
      fetchUserUnits()
    })

    return {
      loading,
      submitting,
      currentPage,
      pageSize,
      total,
      orders,
      searchForm,
      dateRange,
      categoryOptions,
      filteredCategoryOptions,
      filterCategory,
      userUnitOptions,
      fetchUserUnits,
      workflowDialogVisible,
      workflowForm,
      handleSearch,
      resetSearch,
      handleCurrentChange,
      handleSizeChange,
      viewOrder,
      startWorkflow,
      confirmStartWorkflow,
      generateConfirmation,
      canStartWorkflow,
      canGenerateConfirmation,
      getStatusType,
      getStatusText,
      formatDate,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.order-list-container {
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
