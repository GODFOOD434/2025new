import api from '../../api/workflow'

const state = {
  tasks: [],
  currentTask: null,
  total: 0,
  page: 1,
  size: 10
}

const mutations = {
  SET_TASKS(state, { tasks, total, page, size }) {
    state.tasks = tasks
    state.total = total
    state.page = page
    state.size = size
  },
  SET_CURRENT_TASK(state, task) {
    state.currentTask = task
  }
}

const actions = {
  async getTasks({ commit }, { page = 1, size = 10, filters = {} }) {
    try {
      const response = await api.getTasks(page, size, filters)
      const { records, total } = response.data.data
      
      commit('SET_TASKS', {
        tasks: records,
        total,
        page,
        size
      })
      
      return records
    } catch (error) {
      throw error
    }
  },
  
  async startWorkflow({ commit }, data) {
    try {
      const response = await api.startWorkflow(data)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  async completeTask({ commit }, { taskId, data }) {
    try {
      const response = await api.completeTask(taskId, data)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

const getters = {
  tasks: state => state.tasks,
  currentTask: state => state.currentTask,
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
