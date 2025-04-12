import api from '../../api/purchase'

const state = {
  orders: [],
  currentOrder: null,
  total: 0,
  page: 1,
  size: 10
}

const mutations = {
  SET_ORDERS(state, { orders, total, page, size }) {
    state.orders = orders
    state.total = total
    state.page = page
    state.size = size
  },
  SET_CURRENT_ORDER(state, order) {
    state.currentOrder = order
  }
}

const actions = {
  async getOrders({ commit }, { page = 1, size = 10, filters = {} }) {
    try {
      console.log('Store: Fetching orders with params:', { page, size, filters })
      const response = await api.getOrders(page, size, filters)
      console.log('Store: API response:', response.data)

      // 处理后端返回的数据格式
      let orders = [];
      let total = 0;

      if (response.data) {
        // 检查响应数据结构
        if (response.data.data && Array.isArray(response.data.data)) {
          // 如果数据在 data 字段中
          orders = response.data.data;
          total = response.data.total || 0;
        } else if (response.data.data && response.data.data.records) {
          // 如果数据在 data.records 字段中
          orders = response.data.data.records;
          total = response.data.data.total || 0;
        } else if (Array.isArray(response.data)) {
          // 如果数据直接是数组
          orders = response.data;
          total = response.data.length;
        } else {
          console.warn('Unexpected API response format:', response.data);
        }
      }

      console.log('Store: Processed orders:', { count: orders.length, total })

      commit('SET_ORDERS', {
        orders,
        total,
        page,
        size
      })

      return orders
    } catch (error) {
      throw error
    }
  },

  async getOrderById({ commit }, id) {
    try {
      const response = await api.getOrderById(id)
      commit('SET_CURRENT_ORDER', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async importOrders({ commit }, formData) {
    try {
      const response = await api.importOrders(formData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async updateOrder({ commit }, { id, data }) {
    try {
      const response = await api.updateOrder(id, data)
      commit('SET_CURRENT_ORDER', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async getUserUnits({ commit }) {
    try {
      const response = await api.getUserUnits()
      console.log('User units response:', response)
      return response.data.data
    } catch (error) {
      console.error('Error fetching user units:', error)
      throw error
    }
  }
}

const getters = {
  orders: state => state.orders,
  currentOrder: state => state.currentOrder,
  total: state => state.total,
  page: state => state.page,
  size: state => state.size
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
