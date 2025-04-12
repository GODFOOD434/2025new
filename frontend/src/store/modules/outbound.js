import api from '../../api/outbound'

const state = {
  outbounds: [],
  currentOutbound: null,
  total: 0,
  page: 1,
  size: 10,
  auditRecords: [],
  currentAuditRecord: null,
  auditTotal: 0,
  auditPage: 1,
  auditSize: 10
}

const mutations = {
  SET_OUTBOUNDS(state, { outbounds, total, page, size }) {
    state.outbounds = outbounds
    state.total = total
    state.page = page
    state.size = size
  },
  SET_CURRENT_OUTBOUND(state, outbound) {
    state.currentOutbound = outbound
  },
  SET_AUDIT_RECORDS(state, { records, total, page, size }) {
    state.auditRecords = records
    state.auditTotal = total
    state.auditPage = page
    state.auditSize = size
  },
  SET_CURRENT_AUDIT_RECORD(state, record) {
    state.currentAuditRecord = record
  }
}

const actions = {
  async getOutbounds({ commit }, { page = 1, size = 10, filters = {} }) {
    try {
      console.log('Store: Fetching outbounds with params:', { page, size, filters })
      const response = await api.getOutbounds(page, size, filters)
      console.log('Store: API response:', response)

      // 防止响应数据结构不符合预期
      if (!response || !response.data || !response.data.data) {
        console.warn('Store: Invalid response structure:', response)
        commit('SET_OUTBOUNDS', {
          outbounds: [],
          total: 0,
          page,
          size
        })
        return []
      }

      const { records, total } = response.data.data
      console.log('Store: Extracted records:', records)
      console.log('Store: Records count:', records ? records.length : 0)

      // 确保记录是数组
      const safeRecords = Array.isArray(records) ? records : []

      // 验证每个记录的完整性
      const validatedRecords = safeRecords.map(record => {
        // 确保 items 字段是数组
        if (record && !Array.isArray(record.items)) {
          record.items = []
        }
        return record
      })

      commit('SET_OUTBOUNDS', {
        outbounds: validatedRecords,
        total: total || 0,
        page,
        size
      })

      return validatedRecords
    } catch (error) {
      console.error('Store: Error fetching outbounds:', error)
      // 出错时设置空数组，避免前端报错
      commit('SET_OUTBOUNDS', {
        outbounds: [],
        total: 0,
        page,
        size
      })
      throw error
    }
  },

  async getOutboundById({ commit }, id) {
    try {
      const response = await api.getOutboundById(id)
      commit('SET_CURRENT_OUTBOUND', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async importOutbounds({ commit }, formData) {
    try {
      console.log('Store: importOutbounds called with formData')
      const response = await api.importOutbounds(formData)
      console.log('Store: importOutbounds response:', response)
      return response.data
    } catch (error) {
      console.error('Store: importOutbounds error:', error)
      throw error
    }
  },

  async completeOutbound({ commit }, id) {
    try {
      const response = await api.completeOutbound(id)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async deleteOutbound({ commit, dispatch }, { id, reason }) {
    try {
      console.log('Store: Deleting outbound with ID:', id, 'Reason:', reason)
      const response = await api.deleteOutbound(id, reason)
      console.log('Store: Delete response:', response)

      // 刷新列表
      await dispatch('getOutbounds', { page: state.page, size: state.size })

      return response.data
    } catch (error) {
      console.error('Store: Error deleting outbound:', error)
      throw error
    }
  },

  async batchDeleteOutbounds({ commit, dispatch }, { ids, reason }) {
    try {
      console.log('Store: Batch deleting outbounds with IDs:', ids, 'Reason:', reason)
      const response = await api.batchDeleteOutbounds(ids, reason)
      console.log('Store: Batch delete response:', response)

      // 刷新列表
      await dispatch('getOutbounds', { page: state.page, size: state.size })

      return response.data
    } catch (error) {
      console.error('Store: Error batch deleting outbounds:', error)
      throw error
    }
  },

  async getAuditRecords({ commit }, { page = 1, size = 10, filters = {} }) {
    try {
      console.log('Store: Fetching audit records with params:', { page, size, filters })
      const response = await api.getAuditRecords({
        page,
        size,
        ...filters
      })
      console.log('Store: Audit records response:', response)

      const { records, total } = response.data.data

      commit('SET_AUDIT_RECORDS', {
        records,
        total,
        page,
        size
      })

      return response.data
    } catch (error) {
      console.error('Store: Error fetching audit records:', error)
      throw error
    }
  },

  async getAuditRecord({ commit }, id) {
    try {
      console.log('Store: Fetching audit record with ID:', id)
      const response = await api.getAuditRecord(id)
      console.log('Store: Audit record response:', response)

      const record = response.data.data
      commit('SET_CURRENT_AUDIT_RECORD', record)

      return record
    } catch (error) {
      console.error('Store: Error fetching audit record:', error)
      throw error
    }
  }
}

const getters = {
  outbounds: state => state.outbounds,
  auditRecords: state => state.auditRecords,
  currentAuditRecord: state => state.currentAuditRecord,
  auditTotal: state => state.auditTotal,
  currentOutbound: state => state.currentOutbound,
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
