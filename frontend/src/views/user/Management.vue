<template>
  <div class="user-management-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="openCreateDialog">新增用户</el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>

        <el-form-item label="姓名">
          <el-input v-model="searchForm.full_name" placeholder="请输入姓名" clearable />
        </el-form-item>

        <el-form-item label="角色">
          <el-select v-model="searchForm.role_id" placeholder="请选择角色" clearable>
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="请选择状态" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 用户列表 -->
      <el-table
        v-loading="loading"
        :data="users"
        style="width: 100%"
        border
      >
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="role.name" label="角色" width="120" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="200">
          <template #default="scope">
            <el-button type="text" @click="editUser(scope.row)">编辑</el-button>
            <el-button
              type="text"
              @click="toggleUserStatus(scope.row)"
              :disabled="scope.row.is_superuser"
            >
              {{ scope.row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button
              type="text"
              @click="resetUserPassword(scope.row)"
              :disabled="scope.row.is_superuser"
            >
              重置密码
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

    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="userForm"
        :rules="userRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>

        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="userForm.full_name" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" />
        </el-form-item>

        <el-form-item label="部门" prop="department">
          <el-input v-model="userForm.department" />
        </el-form-item>

        <el-form-item label="角色" prop="role_id">
          <el-select v-model="userForm.role_id" placeholder="请选择角色">
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>

        <el-form-item v-if="!isEdit" label="确认密码" prop="confirm_password">
          <el-input v-model="userForm.confirm_password" type="password" show-password />
        </el-form-item>

        <el-form-item label="状态">
          <el-switch
            v-model="userForm.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUser" :loading="submitting">
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
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'UserManagement',

  setup() {
    const store = useStore()
    const formRef = ref(null)

    // 加载状态
    const loading = ref(false)
    const submitting = ref(false)

    // 分页参数
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)

    // 用户数据
    const users = ref([])

    // 角色数据
    const roles = ref([])

    // 搜索表单
    const searchForm = reactive({
      username: '',
      full_name: '',
      role_id: '',
      is_active: ''
    })

    // 对话框状态
    const dialogVisible = ref(false)
    const isEdit = ref(false)
    const userForm = reactive({
      username: '',
      email: '',
      full_name: '',
      phone: '',
      department: '',
      role_id: '',
      password: '',
      confirm_password: '',
      is_active: true
    })

    // 表单验证规则
    const userRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, message: '用户名长度不能小于3个字符', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      full_name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      role_id: [
        { required: true, message: '请选择角色', trigger: 'change' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
      ],
      confirm_password: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== userForm.password) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }

    // 获取用户列表
    const fetchUsers = async () => {
      try {
        loading.value = true

        // 这里假设有一个获取用户列表的API
        // 实际实现可能需要根据后端API调整
        const response = await fetch('/api/users', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${store.getters['auth/token']}`
          }
        })

        const data = await response.json()

        users.value = data.data.records || []
        total.value = data.data.total || 0
      } catch (error) {
        console.error('获取用户列表失败:', error)
        ElMessage.error(error.message || '获取用户列表失败')
      } finally {
        loading.value = false
      }
    }

    // 获取角色列表
    const fetchRoles = async () => {
      try {
        // 这里假设有一个获取角色列表的API
        // 实际实现可能需要根据后端API调整
        const response = await fetch('/api/roles', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${store.getters['auth/token']}`
          }
        })

        const data = await response.json()

        roles.value = data.data || []
      } catch (error) {
        console.error('获取角色列表失败:', error)
        ElMessage.error(error.message || '获取角色列表失败')
      }
    }

    // 搜索
    const handleSearch = () => {
      currentPage.value = 1
      fetchUsers()
    }

    // 重置搜索
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      currentPage.value = 1
      fetchUsers()
    }

    // 处理页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchUsers()
    }

    // 处理每页数量变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchUsers()
    }

    // 打开新增对话框
    const openCreateDialog = () => {
      isEdit.value = false
      Object.keys(userForm).forEach(key => {
        userForm[key] = key === 'is_active' ? true : ''
      })
      dialogVisible.value = true
    }

    // 编辑用户
    const editUser = (user) => {
      isEdit.value = true
      Object.keys(userForm).forEach(key => {
        if (key !== 'password' && key !== 'confirm_password') {
          userForm[key] = user[key]
        } else {
          userForm[key] = ''
        }
      })
      dialogVisible.value = true
    }

    // 保存用户
    const saveUser = async () => {
      try {
        await formRef.value.validate()

        submitting.value = true

        if (isEdit.value) {
          // 更新用户
          await fetch(`/api/users/${userForm.id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${store.getters['auth/token']}`
            },
            body: JSON.stringify({
              email: userForm.email,
              full_name: userForm.full_name,
              phone: userForm.phone,
              department: userForm.department,
              role_id: userForm.role_id,
              is_active: userForm.is_active
            })
          })

          ElMessage.success('用户更新成功')
        } else {
          // 创建用户
          await fetch('/api/users', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${store.getters['auth/token']}`
            },
            body: JSON.stringify({
              username: userForm.username,
              email: userForm.email,
              full_name: userForm.full_name,
              phone: userForm.phone,
              department: userForm.department,
              role_id: userForm.role_id,
              password: userForm.password,
              is_active: userForm.is_active
            })
          })

          ElMessage.success('用户创建成功')
        }

        dialogVisible.value = false
        fetchUsers()
      } catch (error) {
        console.error('保存用户失败:', error)
        ElMessage.error(error.message || '保存用户失败')
      } finally {
        submitting.value = false
      }
    }

    // 切换用户状态
    const toggleUserStatus = (user) => {
      ElMessageBox.confirm(
        `确定要${user.is_active ? '禁用' : '启用'}用户 ${user.username} 吗?`,
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await fetch(`/api/users/${user.id}/status`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${store.getters['auth/token']}`
            },
            body: JSON.stringify({
              is_active: !user.is_active
            })
          })

          ElMessage.success(`用户${user.is_active ? '禁用' : '启用'}成功`)
          fetchUsers()
        } catch (error) {
          console.error('切换用户状态失败:', error)
          ElMessage.error(error.message || '切换用户状态失败')
        }
      }).catch(() => {})
    }

    // 重置用户密码
    const resetUserPassword = (user) => {
      ElMessageBox.prompt(
        '请输入新密码',
        '重置密码',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputType: 'password',
          inputValidator: (value) => {
            if (!value) {
              return '密码不能为空'
            }
            if (value.length < 6) {
              return '密码长度不能小于6个字符'
            }
            return true
          }
        }
      ).then(async ({ value }) => {
        try {
          await fetch(`/api/users/${user.id}/password`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${store.getters['auth/token']}`
            },
            body: JSON.stringify({
              password: value
            })
          })

          ElMessage.success('密码重置成功')
        } catch (error) {
          console.error('重置密码失败:', error)
          ElMessage.error(error.message || '重置密码失败')
        }
      }).catch(() => {})
    }

    // 格式化日期
    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleString()
    }

    // 组件挂载时获取数据
    onMounted(() => {
      fetchUsers()
      fetchRoles()
    })

    return {
      loading,
      submitting,
      currentPage,
      pageSize,
      total,
      users,
      roles,
      searchForm,
      dialogVisible,
      isEdit,
      userForm,
      userRules,
      handleSearch,
      resetSearch,
      handleCurrentChange,
      handleSizeChange,
      openCreateDialog,
      editUser,
      saveUser,
      toggleUserStatus,
      resetUserPassword,
      formatDate
    }
  }
}
</script>

<style scoped>
.user-management-container {
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
