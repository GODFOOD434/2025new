import axios from 'axios'
import { ElMessage } from 'element-plus'
import store from '@/store'
import router from '@/router'

// 创建 axios 实例
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API || '/api', // API 的 base_url
  timeout: 60000, // 请求超时时间增加到60秒
  withCredentials: true, // 跨域请求时发送 cookies
  // 添加重试机制
  retry: 3, // 重试次数
  retryDelay: 1000 // 重试间隔（毫秒）
})

console.log('Axios baseURL:', service.defaults.baseURL)

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    if (store.getters['auth/token']) {
      // 让每个请求携带 token
      config.headers['Authorization'] = `Bearer ${store.getters['auth/token']}`
    }

    // 设置重试配置
    config.retry = config.retry || service.defaults.retry
    config.retryDelay = config.retryDelay || service.defaults.retryDelay

    return config
  },
  error => {
    // 对请求错误做些什么
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    const res = response.data

    // 如果返回的不是 JSON 数据，直接返回
    if (response.headers['content-type'] && response.headers['content-type'].indexOf('application/json') === -1) {
      return response
    }

    // 如果返回的状态码不是 200，说明出错了
    if (res.code && res.code !== 200) {
      // 处理特定错误
      if (res.code === 401) {
        // 未授权，清除 token 并跳转到登录页
        store.dispatch('auth/logout')
        router.push('/login')
        ElMessage.error('登录已过期，请重新登录')
      } else {
        // 其他错误
        ElMessage.error(res.message || '发生错误')
      }
      return Promise.reject(new Error(res.message || '发生错误'))
    }

    return res
  },
  error => {
    // 对响应错误做点什么
    console.error('Response error:', error)

    // 获取配置
    const config = error.config || {}

    // 如果是超时错误或网络错误，并且还有重试次数，则进行重试
    if ((error.code === 'ECONNABORTED' ||
         (error.message && (error.message.includes('timeout') || error.message.includes('Network Error'))) ||
         !error.response) && config.retry) {

      // 重试计数器
      config.__retryCount = config.__retryCount || 0

      // 检查是否超过重试次数
      if (config.__retryCount < config.retry) {
        config.__retryCount += 1
        console.log(`请求重试，第 ${config.__retryCount} 次，共 ${config.retry} 次`)

        // 创建新的Promise来处理重试
        return new Promise(resolve => {
          setTimeout(() => {
            console.log(`重试等待 ${config.retryDelay} ms 后执行`)
            resolve()
          }, config.retryDelay || 1000)
        }).then(() => {
          // 创建新的axios实例来发送请求，避免拦截器循环
          return axios(config)
        })
      }
    }

    // 处理特定错误
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，清除 token 并跳转到登录页
          store.dispatch('auth/logout')
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          // 开发环境下，显示详细错误信息
          if (process.env.NODE_ENV === 'development') {
            ElMessage.error(`服务器错误: ${error.message}`)
          } else {
            ElMessage.error('服务器错误，请稍后再试')
          }
          break
        default:
          ElMessage.error(error.message || '发生错误')
      }
    } else if (error.message && error.message.includes('timeout')) {
      // 超时错误
      ElMessage.error('请求超时，请稍后再试')
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      ElMessage.error('无法连接到服务器，请检查网络连接')
    } else {
      // 请求配置有误
      ElMessage.error('请求配置错误: ' + error.message)
    }

    return Promise.reject(error)
  }
)

// 模拟数据模式
const MOCK_MODE = false // 设置为 false 禁用模拟数据，使用真实后端 API

// 模拟数据处理函数
const handleMockData = (config) => {
  console.log('Using mock data for:', config.url)

  // 根据请求路径返回不同的模拟数据
  if (config.url.includes('/auth/login')) {
    return {
      code: 200,
      data: {
        token: 'mock-token-12345',
        user: {
          id: 1,
          username: 'admin',
          full_name: '管理员',
          email: 'admin@example.com',
          role: {
            id: 1,
            name: '系统管理员'
          }
        }
      },
      message: '登录成功'
    }
  }

  if (config.url.includes('/auth/user')) {
    return {
      code: 200,
      data: {
        id: 1,
        username: 'admin',
        full_name: '管理员',
        email: 'admin@example.com',
        role: {
          id: 1,
          name: '系统管理员'
        }
      }
    }
  }

  if (config.url.includes('/purchase/orders')) {
    return {
      code: 200,
      data: {
        records: [
          {
            id: 1,
            order_no: 'PO-2023-001',
            plan_number: 'PLAN-2023-001',
            order_date: '2023-01-15',
            supplier_name: '供应商A',
            supplier_code: 'SUP-A',
            category: '原材料',
            user_unit: '生产部',
            material_group: 'MG-001',
            first_level_product: '产品A',
            factory: '工厂1',
            delivery_type: 'WAREHOUSE',
            status: 'PENDING',
            total_amount: 10000
          },
          {
            id: 2,
            order_no: 'PO-2023-002',
            plan_number: 'PLAN-2023-002',
            order_date: '2023-02-20',
            supplier_name: '供应商B',
            supplier_code: 'SUP-B',
            category: '设备',
            user_unit: '研发部',
            material_group: 'MG-002',
            first_level_product: '产品B',
            factory: '工厂2',
            delivery_type: 'DIRECT',
            status: 'CONFIRMED',
            total_amount: 20000
          }
        ],
        total: 2,
        size: 10,
        current: 1,
        pages: 1
      }
    }
  }

  if (config.url.includes('/workflow/tasks')) {
    return {
      code: 200,
      data: {
        records: [
          {
            taskId: 'task-001',
            taskName: '采购订单确认',
            businessKey: 'PO-2023-001',
            orderInfo: {
              supplierName: '供应商A',
              category: '原材料',
              userUnit: '生产部'
            },
            createTime: '2023-01-16T10:00:00',
            dueDate: '2023-01-18T10:00:00',
            priority: 'HIGH'
          },
          {
            taskId: 'task-002',
            taskName: '质检确认',
            businessKey: 'PO-2023-002',
            orderInfo: {
              supplierName: '供应商B',
              category: '设备',
              userUnit: '研发部'
            },
            createTime: '2023-02-21T14:30:00',
            dueDate: '2023-02-23T14:30:00',
            priority: 'MEDIUM'
          }
        ],
        total: 2,
        size: 10,
        current: 1,
        pages: 1
      }
    }
  }

  // 默认返回空数据
  return {
    code: 200,
    data: {
      records: [],
      total: 0,
      size: 10,
      current: 1,
      pages: 0
    }
  }
}

// 创建一个包装函数，根据模式决定是使用真实请求还是模拟数据
const request = async (config) => {
  if (MOCK_MODE) {
    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    return handleMockData(config)
  } else {
    return service(config)
  }
}

// 导出请求方法
export default {
  get: (url, params) => request({ method: 'get', url, params }),
  post: (url, data) => request({ method: 'post', url, data }),
  put: (url, data) => request({ method: 'put', url, data }),
  delete: (url, params) => request({ method: 'delete', url, params })
}
