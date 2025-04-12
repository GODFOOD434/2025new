import api from '../../api/notification'

const state = {
  notifications: [],
  unreadCount: 0,
  total: 0
}

const mutations = {
  SET_NOTIFICATIONS(state, { notifications, unreadCount, total }) {
    state.notifications = notifications
    state.unreadCount = unreadCount
    state.total = total
  },
  MARK_AS_READ(state, id) {
    const notification = state.notifications.find(n => n.id === id)
    if (notification) {
      notification.is_read = true
      state.unreadCount = Math.max(0, state.unreadCount - 1)
    }
  },
  MARK_ALL_AS_READ(state) {
    state.notifications.forEach(notification => {
      notification.is_read = true
    })
    state.unreadCount = 0
  }
}

const actions = {
  async getNotifications({ commit }, { isRead = null, type = null } = {}) {
    try {
      const response = await api.getNotifications(isRead, type)
      const { notifications, unread, total } = response.data
      
      commit('SET_NOTIFICATIONS', {
        notifications,
        unreadCount: unread,
        total
      })
      
      return notifications
    } catch (error) {
      throw error
    }
  },
  
  async markAsRead({ commit }, id) {
    try {
      await api.markAsRead(id)
      commit('MARK_AS_READ', id)
    } catch (error) {
      throw error
    }
  },
  
  async markAllAsRead({ commit }) {
    try {
      await api.markAllAsRead()
      commit('MARK_ALL_AS_READ')
    } catch (error) {
      throw error
    }
  },
  
  async createNotification({ dispatch }, data) {
    try {
      await api.createNotification(data)
      dispatch('getNotifications')
    } catch (error) {
      throw error
    }
  },
  
  async deleteNotification({ dispatch }, id) {
    try {
      await api.deleteNotification(id)
      dispatch('getNotifications')
    } catch (error) {
      throw error
    }
  }
}

const getters = {
  notifications: state => state.notifications,
  unreadCount: state => state.unreadCount,
  total: state => state.total
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
