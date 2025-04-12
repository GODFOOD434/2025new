<template>
  <div class="inventory-detail-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>库存详情</span>
          <div class="header-actions">
            <el-button @click="$router.push('/inventory')">返回列表</el-button>
            <el-button type="primary" @click="editInventory">编辑</el-button>
            <el-button type="success" @click="adjustInventory">调整库存</el-button>
          </div>
        </div>
      </template>

      <div v-if="inventory">
        <!-- 基本信息 -->
        <h3>基本信息</h3>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="物料编码">{{ inventory.material_code }}</el-descriptions-item>
          <el-descriptions-item label="物料描述">{{ inventory.material_description }}</el-descriptions-item>
          <el-descriptions-item label="大类">{{ inventory.category }}</el-descriptions-item>
          <el-descriptions-item label="计量单位">{{ inventory.unit }}</el-descriptions-item>
          <el-descriptions-item label="库存数量">{{ inventory.quantity }}</el-descriptions-item>
          <el-descriptions-item label="库位">{{ inventory.location }}</el-descriptions-item>
          <el-descriptions-item label="单价">{{ formatCurrency(inventory.unit_price) }}</el-descriptions-item>
          <el-descriptions-item label="总价值">{{ formatCurrency(inventory.total_value) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 事务记录 -->
        <h3>事务记录</h3>
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

      <div v-else-if="!loading" class="empty-data">
        未找到库存信息
      </div>
    </el-card>

    <!-- 编辑库存对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑库存"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="inventoryForm"
        :rules="inventoryRules"
        label-width="100px"
      >
        <el-form-item label="物料编码" prop="material_code">
          <el-input v-model="inventoryForm.material_code" disabled />
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

        <el-form-item label="库位" prop="location">
          <el-input v-model="inventoryForm.location" />
        </el-form-item>

        <el-form-item label="单价" prop="unit_price">
          <el-input-number v-model="inventoryForm.unit_price" :min="0" :precision="2" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveInventory" :loading="submitting">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 调整库存对话框 -->
    <el-dialog
      v-model="adjustDialogVisible"
      title="调整库存"
      width="600px"
    >
      <el-form
        ref="adjustFormRef"
        :model="adjustForm"
        :rules="adjustRules"
        label-width="100px"
      >
        <el-form-item label="物料编码">
          <el-input v-model="inventory.material_code" disabled />
        </el-form-item>

        <el-form-item label="物料描述">
          <el-input v-model="inventory.material_description" disabled />
        </el-form-item>

        <el-form-item label="当前库存">
          <el-input v-model="inventory.quantity" disabled />
        </el-form-item>

        <el-form-item label="调整类型" prop="adjustType">
          <el-radio-group v-model="adjustForm.adjustType">
            <el-radio label="INBOUND">入库</el-radio>
            <el-radio label="OUTBOUND">出库</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="调整数量" prop="quantity">
          <el-input-number v-model="adjustForm.quantity" :min="0" />
        </el-form-item>

        <el-form-item label="参考单号" prop="reference_no">
          <el-input v-model="adjustForm.reference_no" placeholder="例如：手动调整" />
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="adjustForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入调整原因"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="adjustDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAdjustment" :loading="submitting">
            保存
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
import { ElMessage } from 'element-plus'

export default {
  name: 'InventoryDetail',

  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    const formRef = ref(null)
    const adjustFormRef = ref(null)

    // 加载状态
    const loading = computed(() => store.getters.isLoading)
    const submitting = ref(false)
    const transactionsLoading = ref(false)

    // 库存数据
    const inventory = computed(() => store.getters['inventory/currentInventory'])

    // 事务记录
    const transactions = ref([])
    const transactionsPage = ref(1)
    const transactionsTotal = ref(0)

    // 编辑对话框
    const editDialogVisible = ref(false)
    const inventoryForm = reactive({
      material_code: '',
      material_description: '',
      category: '',
      unit: '',
      location: '',
      unit_price: 0
    })

    // 表单验证规则
    const inventoryRules = {
      material_description: [
        { required: true, message: '请输入物料描述', trigger: 'blur' }
      ],
      unit: [
        { required: true, message: '请输入计量单位', trigger: 'blur' }
      ]
    }

    // 调整库存对话框
    const adjustDialogVisible = ref(false)
    const adjustForm = reactive({
      adjustType: 'INBOUND',
      quantity: 0,
      reference_no: '手动调整',
      remark: ''
    })

    // 调整表单验证规则
    const adjustRules = {
      quantity: [
        { required: true, message: '请输入调整数量', trigger: 'blur' },
        { type: 'number', min: 0.01, message: '调整数量必须大于0', trigger: 'blur' }
      ],
      remark: [
        { required: true, message: '请输入调整原因', trigger: 'blur' }
      ]
    }

    // 获取库存详情
    const fetchInventoryDetail = async () => {
      try {
        const id = route.params.id
        if (id) {
          await store.dispatch('inventory/getInventoryById', id)
          await fetchTransactions()
        }
      } catch (error) {
        console.error('获取库存详情失败:', error)
        ElMessage.error(error.message || '获取库存详情失败')
      }
    }

    // 获取事务记录
    const fetchTransactions = async () => {
      if (!inventory.value) return

      try {
        transactionsLoading.value = true

        const response = await store.dispatch('inventory/getTransactions', {
          page: transactionsPage.value,
          size: 10,
          filters: {
            inventory_id: inventory.value.id
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

    // 编辑库存
    const editInventory = () => {
      if (!inventory.value) return

      Object.keys(inventoryForm).forEach(key => {
        inventoryForm[key] = inventory.value[key]
      })

      editDialogVisible.value = true
    }

    // 保存库存
    const saveInventory = async () => {
      try {
        await formRef.value.validate()

        submitting.value = true

        await store.dispatch('inventory/updateInventory', {
          id: inventory.value.id,
          data: inventoryForm
        })

        ElMessage.success('库存更新成功')
        editDialogVisible.value = false
        fetchInventoryDetail()
      } catch (error) {
        console.error('保存库存失败:', error)
        ElMessage.error(error.message || '保存库存失败')
      } finally {
        submitting.value = false
      }
    }

    // 调整库存
    const adjustInventory = () => {
      if (!inventory.value) return

      adjustForm.adjustType = 'INBOUND'
      adjustForm.quantity = 0
      adjustForm.reference_no = '手动调整'
      adjustForm.remark = ''

      adjustDialogVisible.value = true
    }

    // 保存调整
    const saveAdjustment = async () => {
      try {
        await adjustFormRef.value.validate()

        submitting.value = true

        // 计算新的库存数量
        let newQuantity = inventory.value.quantity
        if (adjustForm.adjustType === 'INBOUND') {
          newQuantity += adjustForm.quantity
        } else {
          newQuantity -= adjustForm.quantity

          // 检查库存是否足够
          if (newQuantity < 0) {
            ElMessage.error('库存不足，无法出库')
            submitting.value = false
            return
          }
        }

        // 更新库存
        await store.dispatch('inventory/updateInventory', {
          id: inventory.value.id,
          data: {
            quantity: newQuantity
          }
        })

        // 创建事务记录
        // 这里假设有一个创建事务记录的API
        // 实际实现可能需要根据后端API调整
        await fetch(`/api/inventory/transactions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            inventory_id: inventory.value.id,
            transaction_type: adjustForm.adjustType,
            quantity: adjustForm.quantity,
            reference_no: adjustForm.reference_no,
            reference_type: '手动调整',
            remark: adjustForm.remark
          })
        })

        ElMessage.success('库存调整成功')
        adjustDialogVisible.value = false
        fetchInventoryDetail()
      } catch (error) {
        console.error('调整库存失败:', error)
        ElMessage.error(error.message || '调整库存失败')
      } finally {
        submitting.value = false
      }
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
      fetchInventoryDetail()
    })

    return {
      loading,
      submitting,
      transactionsLoading,
      inventory,
      transactions,
      transactionsPage,
      transactionsTotal,
      editDialogVisible,
      inventoryForm,
      inventoryRules,
      adjustDialogVisible,
      adjustForm,
      adjustRules,
      handleTransactionsPageChange,
      editInventory,
      saveInventory,
      adjustInventory,
      saveAdjustment,
      formatDate,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.inventory-detail-container {
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

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>
