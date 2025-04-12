import api from '../../api/inventory'

const state = {
  inventories: [],
  currentInventory: null,
  transactions: [],
  total: 0,
  page: 1,
  size: 10
}

const mutations = {
  SET_INVENTORIES(state, { inventories, total, page, size }) {
    state.inventories = inventories
    state.total = total
    state.page = page
    state.size = size
  },
  SET_CURRENT_INVENTORY(state, inventory) {
    state.currentInventory = inventory
  },
  SET_TRANSACTIONS(state, transactions) {
    state.transactions = transactions
  }
}

const actions = {
  async getInventories({ commit }, { page = 1, size = 10, filters = {} }) {
    try {
      const response = await api.getInventories(page, size, filters)

      // 增强错误处理，确保响应数据结构符合预期
      if (!response || !response.data || !response.data.data) {
        console.warn('Invalid inventory response structure:', response)
        commit('SET_INVENTORIES', {
          inventories: [],
          total: 0,
          page,
          size
        })
        return { data: { records: [] } }
      }

      const { records = [], total = 0 } = response.data.data

      commit('SET_INVENTORIES', {
        inventories: records,
        total,
        page,
        size
      })

      return response
    } catch (error) {
      console.error('Error fetching inventories:', error)
      commit('SET_INVENTORIES', {
        inventories: [],
        total: 0,
        page,
        size
      })
      // 返回一个空的响应对象，避免调用者出错
      return { data: { records: [] } }
    }
  },

  async getInventoryById({ commit }, id) {
    try {
      const response = await api.getInventoryById(id)
      commit('SET_CURRENT_INVENTORY', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async createInventory({ commit }, data) {
    try {
      const response = await api.createInventory(data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async updateInventory({ commit }, { id, data }) {
    try {
      const response = await api.updateInventory(id, data)
      commit('SET_CURRENT_INVENTORY', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async getTransactions({ commit }, { page = 1, size = 10, filters = {} }) {
    try {
      const response = await api.getTransactions(page, size, filters)
      const { records } = response.data.data
      commit('SET_TRANSACTIONS', records)
      return records
    } catch (error) {
      throw error
    }
  }
}

const getters = {
  inventories: state => state.inventories,
  currentInventory: state => state.currentInventory,
  transactions: state => state.transactions,
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
