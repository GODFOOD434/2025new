import axios from 'axios'
import store from '../store'
import router from '../router'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',  // 使用绝对 URL
  timeout: 30000,
  withCredentials: false,  // 不使用 withCredentials，避免 CORS 问题
  headers: {
    'Content-Type': 'application/json'
  }
})

console.log('API baseURL:', api.defaults.baseURL)

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 显示加载状态
    store.dispatch('setLoading', true)

    // 添加token到请求头
    const token = store.getters['auth/token']
    console.log('Request interceptor - token:', token)
    console.log('Request URL:', config.url)

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('Added Authorization header:', config.headers.Authorization)
    } else {
      console.warn('No token available for request')
    }

    return config
  },
  error => {
    // 隐藏加载状态
    store.dispatch('setLoading', false)

    // 处理请求错误
    store.dispatch('setError', error.message)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 隐藏加载状态
    store.dispatch('setLoading', false)

    return response
  },
  error => {
    // 隐藏加载状态
    store.dispatch('setLoading', false)

    // 处理响应错误
    if (error.response) {
      const { status, data } = error.response
      console.error(`API 错误 (${status}):`, data)

      // 处理401错误（未授权）
      if (status === 401) {
        store.dispatch('auth/logout')
        router.push('/login')
      }

      // 处理500错误（服务器错误）
      else if (status === 500) {
        console.error('服务器错误详情:', data)
      }

      // 处理404错误（资源不存在）
      else if (status === 404) {
        console.error('资源不存在:', error.config?.url)
      }

      // 设置错误信息
      const errorMessage = data.detail || '请求失败'
      store.dispatch('setError', errorMessage)
    } else if (error.request) {
      // 请求发出但没有收到响应
      console.error('网络错误: 服务器没有响应', error.request)
      store.dispatch('setError', '服务器没有响应，请检查网络连接')
    } else {
      // 请求设置时发生错误
      console.error('请求错误:', error.message)
      store.dispatch('setError', error.message || '网络错误')
    }

    return Promise.reject(error)
  }
)

export default api
