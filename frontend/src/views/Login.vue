<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>仓储工作流系统</h2>
        <p>请登录您的账号</p>
      </div>

      <el-form
        ref="loginForm"
        :model="loginData"
        :rules="loginRules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginData.username"
            placeholder="请输入用户名"
            prefix-icon="el-icon-user"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginData.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="el-icon-lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

export default {
  name: 'Login',

  setup() {
    const store = useStore()
    const router = useRouter()
    const loginForm = ref(null)

    const loading = computed(() => store.getters.isLoading)

    const loginData = reactive({
      username: 'admin',  // 默认用户名
      password: 'admin'   // 默认密码
    })

    console.log('Initial login data:', loginData)

    const loginRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
      ]
    }

    const handleLogin = async () => {
      try {
        console.log('Login form:', loginForm.value)
        console.log('Login data:', loginData)

        // 验证表单
        const valid = await loginForm.value.validate()
          .catch(err => {
            console.error('Form validation error:', err)
            return false
          })

        if (!valid) {
          console.error('Form validation failed')
          return
        }

        console.log('Form validated, dispatching login action')
        try {
          const result = await store.dispatch('auth/login', {
            username: loginData.username,
            password: loginData.password
          })

          console.log('Login dispatch result:', result)

          // 检查是否成功获取用户信息
          const token = store.getters['auth/token']
          console.log('Token after login:', token)

          if (token) {
            ElMessage.success('登录成功')

            // 尝试手动获取用户信息
            try {
              const userResponse = await axios.get('/api/users/me', {
                headers: {
                  'Authorization': `Bearer ${token}`
                }
              })
              console.log('Manual user info request:', userResponse)

              // 存储用户信息
              store.commit('auth/SET_USER', userResponse.data)
            } catch (userError) {
              console.error('Manual user info request failed:', userError)
            }

            // 无论用户信息是否获取成功，都跳转到首页
            router.push('/')
          } else {
            ElMessage.error('登录成功，但无法获取用户信息')
          }
        } catch (loginError) {
          console.error('Login dispatch error:', loginError)
          ElMessage.error(loginError.message || '登录失败')
        }
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error(error.message || '登录失败，请检查用户名和密码')
      }
    }

    return {
      loginForm,
      loginData,
      loginRules,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-box {
  width: 400px;
  padding: 40px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 0 0 10px;
  font-size: 24px;
  color: #303133;
}

.login-header p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.login-button {
  width: 100%;
}
</style>
