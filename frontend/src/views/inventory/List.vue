<template>
  <div class="inventory-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>库存列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="openCreateDialog">新增库存</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="物料编码">
          <el-input v-model="searchForm.material_code" placeholder="请输入物料编码" clearable />
        </el-form-item>

        <el-form-item label="物料描述">
          <el-input v-model="searchForm.material_description" placeholder="请输入物料描述" clearable />
        </el-form-item>

        <el-form-item label="大类">
          <el-input v-model="searchForm.category" placeholder="请输入大类" clearable />
        </el-form-item>

        <el-form-item label="库位">
          <el-input v-model="searchForm.location" placeholder="请输入库位" clearable />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table
        v-loading="loading"
        :data="inventories"
        style="width: 100%"
        border
      >
        <el-table-column prop="material_code" label="物料编码" width="120" />
        <el-table-column prop="material_description" label="物料描述" min-width="200" />
        <el-table-column prop="category" label="大类" width="120" />
        <el-table-column prop="unit" label="计量单位" width="80" />
        <el-table-column prop="quantity" label="库存数量" width="100">
          <template #default="scope">
            <span :class="{ 'text-warning': scope.row.quantity < 10 }">
              {{ scope.row.quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="库位" width="120" />
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="scope">
            {{ formatCurrency(scope.row.unit_price) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_value" label="总价值" width="120">
          <template #default="scope">
            {{ formatCurrency(scope.row.total_value) }}
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="200">
          <template #default="scope">
            <el-button type="text" @click="viewInventory(scope.row)">查看</el-button>
            <el-button type="text" @click="editInventory(scope.row)">编辑</el-button>
            <el-button type="text" @click="viewTransactions(scope.row)">事务记录</el-button>
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

    <!-- 新增/编辑库存对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑库存' : '新增库存'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="inventoryForm"
        :rules="inventoryRules"
        label-width="100px"
      >
        <el-form-item label="物料编码" prop="material_code">
          <el-input v-model="inventoryForm.material_code" :disabled="isEdit" />
        </el-form-item>

        <el-form-item label="物料描述" prop="material_description">
          <el-input v-model="inventoryForm.material_description" />
        </el-form-item>

        <el-form-item label="大类" prop="category">
          <el-input v-model="inventoryForm.category" />
        </el-form-item>

        <el-form-item label="计量单位" prop="unit">
          <el-input v-model="inventoryForm.unit" />
        </el-form-item>

        <el-form-item label="库存数量" prop="quantity">
          <el-input-number v-model="inventoryForm.quantity" :min="0" />
        </el-form-item>

        <el-form-item label="库位" prop="location">
          <el-input v-model="inventoryForm.location" />
        </el-form-item>

        <el-form-item label="单价" prop="unit_price">
          <el-input-number v-model="inventoryForm.unit_price" :min="0" :precision="2" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveInventory" :loading="submitting">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 事务记录对话框 -->
    <el-dialog
      v-model="transactionDialogVisible"
      title="库存事务记录"
      width="800px"
    >
      <div v-if="currentInventory">
        <h3>{{ currentInventory.material_code }} - {{ currentInventory.material_description }}</h3>

        <el-table
          v-loading="transactionsLoading"
          :data="transactions"
          style="width: 100%"
          border
        >
          <el-table-column prop="transaction_time" label="事务时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.transaction_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="transaction_type" label="事务类型" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.transaction_type === 'INBOUND' ? 'success' : 'danger'">
                {{ scope.row.transaction_type === 'INBOUND' ? '入库' : '出库' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="100" />
          <el-table-column prop="reference_no" label="参考单号" width="150" />
          <el-table-column prop="reference_type" label="参考类型" width="120" />
          <el-table-column prop="operator" label="操作人" width="120" />
          <el-table-column prop="remark" label="备注" min-width="200" />
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            background
            layout="total, prev, pager, next"
            :total="transactionsTotal"
            :page-size="10"
            :current-page="transactionsPage"
            @current-change="handleTransactionsPageChange"
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'InventoryList',

  setup() {
    const store = useStore()
    const router = useRouter()
    const formRef = ref(null)

    // 加载状态
    const loading = computed(() => store.getters.isLoading)
    const submitting = ref(false)
    const transactionsLoading = ref(false)

    // 分页参数
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = computed(() => store.getters['inventory/total'])

    // 库存数据
    const inventories = computed(() => store.getters['inventory/inventories'])

    // 搜索表单
    const searchForm = reactive({
      material_code: '',
      material_description: '',
      category: '',
      location: ''
    })

    // 对话框状态
    const dialogVisible = ref(false)
    const isEdit = ref(false)
    const inventoryForm = reactive({
      material_code: '',
      material_description: '',
      category: '',
      unit: '',
      quantity: 0,
      location: '',
      unit_price: 0
    })

    // 表单验证规则
    const inventoryRules = {
      material_code: [
        { required: true, message: '请输入物料编码', trigger: 'blur' }
      ],
      material_description: [
        { required: true, message: '请输入物料描述', trigger: 'blur' }
      ],
      unit: [
        { required: true, message: '请输入计量单位', trigger: 'blur' }
      ]
    }

    // 事务记录对话框
    const transactionDialogVisible = ref(false)
    const currentInventory = ref(null)
    const transactions = ref([])
    const transactionsPage = ref(1)
    const transactionsTotal = ref(0)

    // 获取库存列表
    const fetchInventories = async () => {
      try {
        await store.dispatch('inventory/getInventories', {
          page: currentPage.value,
          size: pageSize.value,
          filters: searchForm
        })
      } catch (error) {
        console.error('获取库存列表失败:', error)
        ElMessage.error(error.message || '获取库存列表失败')
      }
    }

    // 搜索
    const handleSearch = () => {
      currentPage.value = 1
      fetchInventories()
    }

    // 重置搜索
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      currentPage.value = 1
      fetchInventories()
    }

    // 处理页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchInventories()
    }

    // 处理每页数量变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchInventories()
    }

    // 查看库存详情
    const viewInventory = (inventory) => {
      router.push(`/inventory/${inventory.id}`)
    }

    // 打开新增对话框
    const openCreateDialog = () => {
      isEdit.value = false
      Object.keys(inventoryForm).forEach(key => {
        inventoryForm[key] = key === 'quantity' || key === 'unit_price' ? 0 : ''
      })
      dialogVisible.value = true
    }

    // 编辑库存
    const editInventory = (inventory) => {
      isEdit.value = true
      Object.keys(inventoryForm).forEach(key => {
        inventoryForm[key] = inventory[key]
      })
      dialogVisible.value = true
    }

    // 保存库存
    const saveInventory = async () => {
      try {
        await formRef.value.validate()

        submitting.value = true

        if (isEdit.value) {
          await store.dispatch('inventory/updateInventory', {
            id: currentInventory.value.id,
            data: inventoryForm
          })
          ElMessage.success('库存更新成功')
        } else {
          await store.dispatch('inventory/createInventory', inventoryForm)
          ElMessage.success('库存创建成功')
        }

        dialogVisible.value = false
        fetchInventories()
      } catch (error) {
        console.error('保存库存失败:', error)
        ElMessage.error(error.message || '保存库存失败')
      } finally {
        submitting.value = false
      }
    }

    // 查看事务记录
    const viewTransactions = async (inventory) => {
      currentInventory.value = inventory
      transactionsPage.value = 1
      transactionDialogVisible.value = true
      await fetchTransactions()
    }

    // 获取事务记录
    const fetchTransactions = async () => {
      if (!currentInventory.value) return

      try {
        transactionsLoading.value = true

        const response = await store.dispatch('inventory/getTransactions', {
          page: transactionsPage.value,
          size: 10,
          filters: {
            inventory_id: currentInventory.value.id
          }
        })

        transactions.value = response.data.records || []
        transactionsTotal.value = response.data.total || 0
      } catch (error) {
        console.error('获取事务记录失败:', error)
        ElMessage.error(error.message || '获取事务记录失败')
      } finally {
        transactionsLoading.value = false
      }
    }

    // 处理事务记录分页变化
    const handleTransactionsPageChange = (page) => {
      transactionsPage.value = page
      fetchTransactions()
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
      fetchInventories()
    })

    return {
      loading,
      submitting,
      transactionsLoading,
      currentPage,
      pageSize,
      total,
      inventories,
      searchForm,
      dialogVisible,
      isEdit,
      inventoryForm,
      inventoryRules,
      transactionDialogVisible,
      currentInventory,
      transactions,
      transactionsPage,
      transactionsTotal,
      handleSearch,
      resetSearch,
      handleCurrentChange,
      handleSizeChange,
      viewInventory,
      openCreateDialog,
      editInventory,
      saveInventory,
      viewTransactions,
      handleTransactionsPageChange,
      formatDate,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.inventory-list-container {
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

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.text-warning {
  color: #E6A23C;
}
</style>
