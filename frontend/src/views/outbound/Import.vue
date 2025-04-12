<template>
  <div class="outbound-import-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>导入出库单</span>
          <el-button @click="$router.push('/outbound')">返回列表</el-button>
        </div>
      </template>

      <el-alert
        v-if="importResult"
        :title="importResult.success ? '导入成功' : '导入失败'"
        :type="importResult.success ? 'success' : 'error'"
        :description="getResultDescription()"
        show-icon
        :closable="false"
        style="margin-bottom: 20px"
      />

      <el-form label-position="top" :model="formData">
        <el-form-item label="采购订单号" prop="purchaseOrderNo">
          <el-input
            v-model="formData.purchaseOrderNo"
            placeholder="请输入采购订单号"
            clearable
            style="width: 300px"
          />
          <div class="form-tip">该采购订单号将应用于所有导入的出库项，无需在Excel文件中填写</div>
        </el-form-item>

        <el-form-item label="选择Excel文件">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            :file-list="fileList"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                请上传Excel文件(.xlsx, .xls)，文件大小不超过10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleImport" :loading="importing" :disabled="!selectedFile">
            开始导入
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 导入结果 -->
      <div v-if="importResult && importResult.data">
        <h3>导入结果</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="导入ID">{{ importResult.data.importId }}</el-descriptions-item>
          <el-descriptions-item label="总记录数">{{ importResult.data.totalCount }}</el-descriptions-item>
          <el-descriptions-item label="成功记录数">{{ importResult.data.successCount }}</el-descriptions-item>
          <el-descriptions-item label="失败记录数">{{ importResult.data.errorCount }}</el-descriptions-item>
        </el-descriptions>

        <!-- 错误详情 -->
        <div v-if="importResult.data.errorCount > 0" class="error-details">
          <h4>错误详情</h4>
          <el-table :data="importResult.data.errorDetails" style="width: 100%" border>
            <el-table-column prop="rowIndex" label="行号" width="80" />
            <el-table-column prop="errorMessage" label="错误信息" />
          </el-table>
        </div>
      </div>

      <!-- 导入说明 -->
      <div class="import-guide">
        <h3>导入说明</h3>
        <p>1. Excel文件必须包含以下必填字段：物料凭证、物料编码、实拨数量、具体用料部门</p>
        <p>2. 导入前请确保物料编码在系统中存在，且库存充足</p>
        <p>3. 导入成功后，出库单状态为"待处理"，需要在出库单列表中完成出库操作</p>
        <p>4. 出库操作完成后，系统将自动更新库存数据</p>
        <p>5. 采购订单号请在上方输入框中填写，将应用于所有导入的出库项</p>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

export default {
  name: 'OutboundImport',

  components: {
    UploadFilled
  },

  setup() {
    const store = useStore()

    const fileList = ref([])
    const selectedFile = ref(null)
    const importing = ref(false)
    const importResult = ref(null)

    // 表单数据
    const formData = reactive({
      purchaseOrderNo: ''
    })

    // 处理文件变化
    const handleFileChange = (file) => {
      const isExcel = file.raw.type === 'application/vnd.ms-excel' ||
                      file.raw.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      const isLt10M = file.raw.size / 1024 / 1024 < 10

      if (!isExcel) {
        ElMessage.error('只能上传Excel文件!')
        fileList.value = []
        selectedFile.value = null
        return
      }

      if (!isLt10M) {
        ElMessage.error('文件大小不能超过10MB!')
        fileList.value = []
        selectedFile.value = null
        return
      }

      selectedFile.value = file.raw
    }

    // 处理导入
    const handleImport = async () => {
      if (!selectedFile.value) {
        ElMessage.warning('请先选择文件')
        return
      }

      try {
        importing.value = true

        // 检查文件类型，支持大小写扩展名
        const fileName = selectedFile.value.name
        const fileNameLower = fileName.toLowerCase()
        if (!fileNameLower.endsWith('.xls') && !fileNameLower.endsWith('.xlsx')) {
          ElMessage.error('只支持Excel文件(.xls, .xlsx, .XLS, .XLSX)')
          importing.value = false
          return
        }

        console.log('Selected file:', selectedFile.value)

        const uploadData = new FormData()
        uploadData.append('file', selectedFile.value)
        uploadData.append('purchase_order_no', formData.purchaseOrderNo)

        // 打印请求内容
        console.log('FormData created with file:', selectedFile.value.name, selectedFile.value.type, selectedFile.value.size)

        try {
          const result = await store.dispatch('outbound/importOutbounds', uploadData)
          console.log('Import result:', result)
          importResult.value = result
        } catch (importError) {
          console.error('Import error details:', importError)
          ElMessage.error(`导入失败: ${importError.message || '服务器错误'}`)
          if (importError.response && importError.response.data) {
            console.error('Server error details:', importError.response.data)
          }
          throw importError
        }

        if (importResult.value && importResult.value.success) {
          ElMessage.success('导入成功')
          if (importResult.value.data) {
            console.log(`成功导入 ${importResult.value.data.successCount} 条数据`)
          }
        } else if (importResult.value) {
          if (importResult.value.data && importResult.value.data.errorCount > 0) {
            ElMessage.warning(`导入部分成功: 成功 ${importResult.value.data.successCount} 条，失败 ${importResult.value.data.errorCount} 条`)
          } else {
            ElMessage.error('导入失败')
          }
        }
      } catch (error) {
        console.error('导入失败:', error)
        ElMessage.error(error.message || '导入失败')
      } finally {
        importing.value = false
      }
    }

    // 重置表单
    const resetForm = () => {
      fileList.value = []
      selectedFile.value = null
      importResult.value = null
      formData.purchaseOrderNo = ''
    }

    // 获取结果描述
    const getResultDescription = () => {
      if (!importResult.value) return ''

      if (importResult.value.success) {
        return `成功导入${importResult.value.data.successCount}条记录，失败${importResult.value.data.errorCount}条记录`
      } else {
        return importResult.value.message || '导入失败'
      }
    }

    return {
      fileList,
      selectedFile,
      importing,
      importResult,
      formData,
      handleFileChange,
      handleImport,
      resetForm,
      getResultDescription
    }
  }
}
</script>

<style scoped>
.outbound-import-container {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.error-details {
  margin-top: 20px;
}

.error-details h4 {
  margin-bottom: 10px;
}

.import-guide {
  margin-top: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.import-guide h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: #303133;
}

.import-guide p {
  margin: 8px 0;
  color: #606266;
}
</style>
