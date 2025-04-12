<template>
  <div class="order-import-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>导入采购订单</span>
          <el-button @click="$router.push('/purchase')">返回列表</el-button>
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

      <el-form label-position="top">
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
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

export default {
  name: 'OrderImport',

  components: {
    UploadFilled
  },

  setup() {
    const store = useStore()

    const fileList = ref([])
    const selectedFile = ref(null)
    const importing = ref(false)
    const importResult = ref(null)

    // 处理文件变化
    const handleFileChange = (file) => {
      console.log('File changed:', file)

      if (!file || !file.raw) {
        ElMessage.error('文件无效!')
        fileList.value = []
        selectedFile.value = null
        return
      }

      // 检查文件类型
      const fileName = file.raw.name || ''
      const fileExt = fileName.toLowerCase().split('.').pop()
      const isExcelExt = fileExt === 'xlsx' || fileExt === 'xls'

      // 检查MIME类型
      const isExcelMime = file.raw.type === 'application/vnd.ms-excel' ||
                      file.raw.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

      // 检查文件大小
      const isLt10M = file.raw.size / 1024 / 1024 < 10

      console.log('File validation:', {
        name: fileName,
        extension: fileExt,
        isExcelExt,
        type: file.raw.type,
        isExcelMime,
        size: file.raw.size,
        isLt10M
      })

      // 如果扩展名或MIME类型不匹配
      if (!isExcelExt && !isExcelMime) {
        ElMessage.error('只能上传Excel文件(.xlsx, .xls)!')
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
      console.log('Selected file:', selectedFile.value)
    }

    // 处理导入
    const handleImport = async () => {
      if (!selectedFile.value) {
        ElMessage.warning('请先选择文件')
        return
      }

      try {
        importing.value = true
        console.log('Starting import with file:', selectedFile.value.name)

        const formData = new FormData()
        formData.append('file', selectedFile.value)

        console.log('FormData created with file:', selectedFile.value.name, selectedFile.value.type, selectedFile.value.size)

        // 显示开始导入的提示
        ElMessage.info('正在导入文件，请稍候...')

        const result = await store.dispatch('purchase/importOrders', formData)
        console.log('Import result:', result)
        importResult.value = result

        if (result.success) {
          ElMessage.success(`导入成功，共${result.data.totalCount}条记录，成功${result.data.successCount}条，失败${result.data.errorCount}条`)
        } else {
          ElMessage.error('导入失败')
        }
      } catch (error) {
        console.error('导入失败:', error)

        // 增强错误处理
        let errorMessage = '导入失败'

        if (error.response && error.response.data) {
          // 如果有详细的错误信息，显示它
          errorMessage = error.response.data.detail || error.response.data.message || errorMessage
        } else if (error.message) {
          // 如果有错误消息，显示它
          errorMessage = error.message

          // 处理超时错误
          if (errorMessage.includes('timeout')) {
            errorMessage = '请求超时，请检查文件大小或网络连接'
          }
        }

        // 显示错误消息
        ElMessage.error(errorMessage)

        // 初始化空的导入结果，以显示错误信息
        importResult.value = {
          success: false,
          data: {
            totalCount: 0,
            successCount: 0,
            errorCount: 1,
            errorDetails: [{
              rowIndex: 0,
              errorMessage: errorMessage
            }],
            importId: ''
          }
        }
      } finally {
        importing.value = false
      }
    }

    // 重置表单
    const resetForm = () => {
      fileList.value = []
      selectedFile.value = null
      importResult.value = null
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
      handleFileChange,
      handleImport,
      resetForm,
      getResultDescription
    }
  }
}
</script>

<style scoped>
.order-import-container {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-details {
  margin-top: 20px;
}

.error-details h4 {
  margin-bottom: 10px;
}
</style>
