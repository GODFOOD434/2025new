import api from './index'

export default {
  /**
   * 用户登录
   * @param {Object} credentials - 登录凭证
   * @param {string} credentials.username - 用户名
   * @param {string} credentials.password - 密码
   * @returns {Promise} - 返回登录结果
   */
  login(credentials) {
    console.log('Login credentials:', credentials)

    // 创建 FormData
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    // 设置特定的请求头，适用于 Chrome
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }

    console.log('Sending login request to:', '/login/access-token')
    return api.post('/login/access-token', formData, config)
      .then(response => {
        console.log('Login response:', response)
        return response
      })
      .catch(error => {
        console.error('Login API error:', error.response || error)
        // 打印更详细的错误信息
        if (error.response) {
          console.error('Error response data:', error.response.data)
          console.error('Error response status:', error.response.status)
          console.error('Error response headers:', error.response.headers)
        } else if (error.request) {
          console.error('Error request:', error.request)
        } else {
          console.error('Error message:', error.message)
        }
        throw error
      })
  },

  /**
   * 获取当前用户信息
   * @returns {Promise} - 返回用户信息
   */
  getUserInfo() {
    console.log('API getUserInfo - calling /users/me')
    // 获取当前 token
    const token = localStorage.getItem('token')
    console.log('Current token from localStorage:', token)

    // 手动设置请求头
    const headers = {
      'Authorization': `Bearer ${token}`
    }
    console.log('Manual headers:', headers)

    return api.get('/users/me', { headers })
      .then(response => {
        console.log('API getUserInfo - success:', response)
        return response
      })
      .catch(error => {
        console.error('API getUserInfo - error:', error.response || error)
        throw error
      })
  },

  updateUserInfo(userData) {
    console.log('API updateUserInfo - calling /users/me')
    // 获取当前 token
    const token = localStorage.getItem('token')
    console.log('Current token from localStorage:', token)

    // 手动设置请求头
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
    console.log('Manual headers:', headers)

    return api.put('/users/me', userData, { headers })
      .then(response => {
        console.log('API updateUserInfo - success:', response)
        return response
      })
      .catch(error => {
        console.error('API updateUserInfo - error:', error.response || error)
        throw error
      })
  },

  // 注意: 我们已经在上面定义了 updateUserInfo 方法
}
