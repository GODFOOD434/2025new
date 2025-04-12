import api from '../../api/confirmation'

const state = {
  confirmations: [],
  currentConfirmation: null,
  total: 0,
  page: 1,
  size: 10
}

const mutations = {
  SET_CONFIRMATIONS(state, { confirmations, total, page, size }) {
    state.confirmations = confirmations
    state.total = total
    state.page = page
    state.size = size
  },
  SET_CURRENT_CONFIRMATION(state, confirmation) {
    state.currentConfirmation = confirmation
  }
}

const actions = {
  async getConfirmations({ commit }, { page = 1, size = 10, filters = {} }) {
    try {
      const response = await api.getConfirmations(page, size, filters)
      const { records, total } = response.data.data
      
      commit('SET_CONFIRMATIONS', {
        confirmations: records,
        total,
        page,
        size
      })
      
      return records
    } catch (error) {
      throw error
    }
  },
  
  async generateConfirmation({ commit }, orderNo) {
    try {
      const response = await api.generateConfirmation(orderNo)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  async printConfirmation({ commit }, id) {
    try {
      const response = await api.printConfirmation(id)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  async getConfirmationPdf({ commit }, id) {
    try {
      const response = await api.getConfirmationPdf(id)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

const getters = {
  confirmations: state => state.confirmations,
  currentConfirmation: state => state.currentConfirmation,
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
