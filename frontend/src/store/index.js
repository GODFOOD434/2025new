import { createStore } from 'vuex'
import auth from './modules/auth'
import purchase from './modules/purchase'
import workflow from './modules/workflow'
import confirmation from './modules/confirmation'
import outbound from './modules/outbound'
import inventory from './modules/inventory'
import report from './modules/report'
import notification from './modules/notification'

export default createStore({
  state: {
    loading: false,
    error: null
  },
  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  actions: {
    setLoading({ commit }, loading) {
      commit('SET_LOADING', loading)
    },
    setError({ commit }, error) {
      commit('SET_ERROR', error)
    }
  },
  getters: {
    isLoading: state => state.loading,
    error: state => state.error
  },
  modules: {
    auth,
    purchase,
    workflow,
    confirmation,
    outbound,
    inventory,
    report,
    notification
  }
})
