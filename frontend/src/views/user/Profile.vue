<template>
  <div class="user-profile-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="8">
          <div class="user-avatar">
            <el-avatar :size="120" :src="avatarUrl">
              {{ userInitials }}
            </el-avatar>
            <h3>{{ currentUser?.full_name || currentUser?.username || '用户' }}</h3>
            <p>{{ currentUser?.role ? currentUser.role.name : '普通用户' }}</p>
          </div>
        </el-col>

        <el-col :span="16">
          <el-form
            ref="formRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>

            <el-form-item label="姓名" prop="full_name">
              <el-input v-model="profileForm.full_name" />
            </el-form-item>

            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" />
            </el-form-item>

            <el-form-item label="部门" prop="department">
              <el-input v-model="profileForm.department" disabled />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="updating">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>

          <el-divider />

          <h3>修改密码</h3>
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>

            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>

            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="updatePassword" :loading="updatingPassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'UserProfile',

  setup() {
    const store = useStore()
    // 表单引用
    const formRef = ref(null)
    const passwordFormRef = ref(null)

    // 打印表单引用状态，用于调试
    console.log('Initial formRef:', formRef.value)

    // 确保表单引用存在的辅助函数
    const ensureFormRef = async (ref, maxAttempts = 5, interval = 100) => {
      let attempts = 0
      while (!ref.value && attempts < maxAttempts) {
        console.log(`Waiting for form ref, attempt ${attempts + 1}/${maxAttempts}`)
        await new Promise(resolve => setTimeout(resolve, interval))
        attempts++
      }
      return !!ref.value
    }

    // 加载状态
    const updating = ref(false)
    const updatingPassword = ref(false)

    // 当前用户
    const currentUser = computed(() => store.getters['auth/currentUser'])

    // 用户头像
    const avatarUrl = computed(() => currentUser.value?.avatar || '')

    // 用户名首字母
    const userInitials = computed(() => {
      if (!currentUser.value) return ''
      if (currentUser.value.full_name) {
        return currentUser.value.full_name.substring(0, 2).toUpperCase()
      }
      return (currentUser.value.username || '').substring(0, 2).toUpperCase()
    })

    // 个人信息表单
    const profileForm = reactive({
      username: '',
      email: '',
      full_name: '',
      phone: '',
      department: ''
    })

    // 个人信息表单验证规则
    const profileRules = {
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      full_name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ]
    }

    // 密码表单
    const passwordForm = reactive({
      old_password: '',
      new_password: '',
      confirm_password: ''
    })

    // 密码表单验证规则
    const passwordRules = {
      old_password: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      new_password: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
      ],
      confirm_password: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== passwordForm.new_password) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }

    // 初始化表单数据
    const initFormData = () => {
      if (currentUser.value) {
        profileForm.username = currentUser.value.username || ''
        profileForm.email = currentUser.value.email || ''
        profileForm.full_name = currentUser.value.full_name || ''
        profileForm.phone = currentUser.value.phone || ''
        profileForm.department = currentUser.value.department || ''
      }
    }

    // 在组件挂载时初始化数据
    onMounted(() => {
      console.log('Component mounted')
      console.log('formRef in onMounted:', formRef.value)

      // 初始化表单数据
      initFormData()

      // 使用 nextTick 确保 DOM 更新后再访问表单引用
      nextTick(() => {
        console.log('formRef after nextTick:', formRef.value)
      })

      // 给表单引用一些时间初始化
      setTimeout(() => {
        console.log('formRef after timeout:', formRef.value)
      }, 500)
    })

    // 更新个人信息
    const updateProfile = async () => {
      try {
        console.log('updateProfile called, formRef:', formRef.value)

        // 显示加载状态
        updating.value = true

        // 使用辅助函数确保表单引用存在
        const formRefExists = await ensureFormRef(formRef, 10, 200)

        if (!formRefExists) {
          console.error('Form reference is still null after multiple attempts')
          ElMessage.error('表单引用不存在，请刷新页面后重试')
          updating.value = false
          return
        }

        // 使用 nextTick 确保 DOM 已经更新
        await nextTick()

        // 验证表单
        console.log('Validating form...')
        await formRef.value.validate()
        console.log('Form validation successful')

        try {
          // 准备要更新的用户数据
          const userData = {
            email: profileForm.email,
            full_name: profileForm.full_name
          }

          // 如果有电话号码，添加到请求中
          if (profileForm.phone) {
            userData.phone = profileForm.phone
          }

          // 如果有部门，添加到请求中
          if (profileForm.department) {
            userData.department = profileForm.department
          }

          console.log('Updating user info with data:', userData)

          // 调用更新用户信息的 action
          await store.dispatch('auth/updateUserInfo', userData)

          ElMessage.success('个人信息更新成功')
        } finally {
          updating.value = false
        }
      } catch (error) {
        console.error('更新个人信息失败:', error)
        ElMessage.error(error.message || '更新个人信息失败')
      }
    }

    // 更新密码
    const updatePassword = async () => {
      try {
        console.log('updatePassword called, passwordFormRef:', passwordFormRef.value)

        // 显示加载状态
        updatingPassword.value = true

        // 使用辅助函数确保表单引用存在
        const formRefExists = await ensureFormRef(passwordFormRef, 10, 200)

        if (!formRefExists) {
          console.error('Password form reference is still null after multiple attempts')
          ElMessage.error('表单引用不存在，请刷新页面后重试')
          updatingPassword.value = false
          return
        }

        // 使用 nextTick 确保 DOM 已经更新
        await nextTick()

        // 验证表单
        console.log('Validating password form...')
        await passwordFormRef.value.validate()
        console.log('Password form validation successful')

        try {
          // 准备要更新的密码数据
          const passwordData = {
            password: passwordForm.new_password,
            old_password: passwordForm.old_password
          }

          console.log('Updating password with data:', { ...passwordData, password: '******' })

          // 调用更新用户信息的 action
          await store.dispatch('auth/updateUserInfo', passwordData)

          ElMessage.success('密码更新成功')

          // 清空密码表单
          passwordForm.old_password = ''
          passwordForm.new_password = ''
          passwordForm.confirm_password = ''
        } finally {
          updatingPassword.value = false
        }

        ElMessage.success('密码修改成功')

        // 清空密码表单
        passwordForm.old_password = ''
        passwordForm.new_password = ''
        passwordForm.confirm_password = ''
      } catch (error) {
        console.error('修改密码失败:', error)
        ElMessage.error(error.message || '修改密码失败')
      }
    }

    // 注意: 我们已经在上面添加了 onMounted 钩子

    return {
      currentUser,
      avatarUrl,
      userInitials,
      profileForm,
      profileRules,
      passwordForm,
      passwordRules,
      updating,
      updatingPassword,
      updateProfile,
      updatePassword,
      formRef,
      passwordFormRef
    }
  }
}
</script>

<style scoped>
.user-profile-container {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.user-avatar h3 {
  margin: 15px 0 5px;
  font-size: 18px;
  color: #303133;
}

.user-avatar p {
  margin: 0;
  color: #909399;
}

h3 {
  margin: 20px 0 10px;
  font-size: 18px;
  color: #303133;
}
</style>
