import api from '../../api/auth'

// 检查初始状态
console.log('Auth store initial state:', {
  token: localStorage.getItem('token') || '',
  user: JSON.parse(localStorage.getItem('user') || 'null')
})

// 从 localStorage 获取初始状态
const initialToken = localStorage.getItem('token') || ''
const initialUser = JSON.parse(localStorage.getItem('user') || 'null')

console.log('Auth store - initializing with token:', initialToken)
console.log('Auth store - initializing with user:', initialUser)

const state = {
  token: initialToken,
  user: initialUser
}

const mutations = {
  SET_TOKEN(state, token) {
    console.log('Mutation SET_TOKEN:', token)
    state.token = token
  },
  SET_USER(state, user) {
    console.log('Mutation SET_USER:', user)
    state.user = user
  },
  LOGOUT(state) {
    console.log('Mutation LOGOUT')
    state.token = ''
    state.user = null
  }
}

const actions = {
  async login({ commit, dispatch }, credentials) {
    try {
      const response = await api.login(credentials)
      console.log('Login action - response:', response)

      // 检查响应中是否包含 access_token
      if (!response.data || !response.data.access_token) {
        console.error('Login response does not contain access_token:', response.data)
        throw new Error('Login response does not contain access_token')
      }

      const token = response.data.access_token
      console.log('Login action - token:', token)

      // 保存token到localStorage
      localStorage.setItem('token', token)
      commit('SET_TOKEN', token)

      // 等待一下，确保 token 已经被设置
      await new Promise(resolve => setTimeout(resolve, 100))

      // 尝试获取用户信息
      try {
        return await dispatch('getUserInfo')
      } catch (userInfoError) {
        console.error('Failed to get user info after login:', userInfoError)
        // 即使获取用户信息失败，也认为登录成功
        return { token }
      }
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  },

  async getUserInfo({ commit, state }) {
    try {
      console.log('Getting user info with token:', state.token)
      const response = await api.getUserInfo()
      console.log('User info response:', response)
      const user = response.data

      // 保存用户信息到localStorage
      localStorage.setItem('user', JSON.stringify(user))
      commit('SET_USER', user)

      return user
    } catch (error) {
      console.error('Get user info error:', error.response || error)
      throw error
    }
  },

  async updateUserInfo({ commit, state }, userData) {
    try {
      console.log('Updating user info:', userData)
      const response = await api.updateUserInfo(userData)
      console.log('Update user info response:', response)

      // 获取更新后的用户信息
      const updatedUser = { ...state.user, ...userData }

      // 保存用户信息到localStorage
      localStorage.setItem('user', JSON.stringify(updatedUser))
      commit('SET_USER', updatedUser)

      return updatedUser
    } catch (error) {
      console.error('Update user info error:', error.response || error)
      throw error
    }
  },

  logout({ commit }) {
    // 清除localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('user')

    // 清除状态
    commit('LOGOUT')
  }
}

const getters = {
  isLoggedIn: state => {
    const result = !!state.token
    console.log('Getter isLoggedIn:', result, 'token:', state.token)
    return result
  },
  currentUser: state => {
    console.log('Getter currentUser:', state.user)
    return state.user
  },
  token: state => {
    console.log('Getter token:', state.token)
    return state.token
  },
  isAdmin: state => {
    const result = state.user && state.user.is_superuser
    console.log('Getter isAdmin:', result)
    return result
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
