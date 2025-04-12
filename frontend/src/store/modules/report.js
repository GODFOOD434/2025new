import api from '../../api/report'

const state = {
  leadershipDashboard: null,
  operationDashboard: null
}

const mutations = {
  SET_LEADERSHIP_DASHBOARD(state, data) {
    state.leadershipDashboard = data
  },
  SET_OPERATION_DASHBOARD(state, data) {
    state.operationDashboard = data
  }
}

const actions = {
  async getLeadershipDashboard({ commit }, timeRange = 'MONTH') {
    try {
      const response = await api.getLeadershipDashboard(timeRange)
      commit('SET_LEADERSHIP_DASHBOARD', response.data.data)
      return response.data.data
    } catch (error) {
      throw error
    }
  },
  
  async getOperationDashboard({ commit }) {
    try {
      const response = await api.getOperationDashboard()
      commit('SET_OPERATION_DASHBOARD', response.data.data)
      return response.data.data
    } catch (error) {
      throw error
    }
  }
}

const getters = {
  leadershipDashboard: state => state.leadershipDashboard,
  operationDashboard: state => state.operationDashboard
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
