import api from './index'

export default {
  /**
   * 获取出库单列表
   * @param {number} page - 页码
   * @param {number} size - 每页数量
   * @param {Object} filters - 过滤条件
   * @returns {Promise} - 返回出库单列表
   */
  async getOutbounds(page = 1, size = 10, filters = {}) {
    // 处理日期参数，确保发送正确的格式
    const params = {
      page: parseInt(page, 10),
      size: parseInt(size, 10)
    }

    // 确保分页参数是有效的数字
    if (isNaN(params.page) || params.page < 1) params.page = 1
    if (isNaN(params.size) || params.size < 1) params.size = 20

    // 处理过滤条件
    if (filters.material_voucher) params.material_voucher = filters.material_voucher
    if (filters.material_code) params.material_code = filters.material_code
    if (filters.department) params.department = filters.department
    if (filters.user_unit) params.user_unit = filters.user_unit

    // 处理状态，只在有值时发送
    if (filters.status && filters.status !== '') {
      params.status = filters.status
    }

    // 处理日期，只在有值时发送
    if (filters.start_date && filters.start_date !== '') {
      params.start_date = filters.start_date
    }

    if (filters.end_date && filters.end_date !== '') {
      params.end_date = filters.end_date
    }

    console.log('API: Sending params to outbound/list:', params)

    try {
      const response = await api.get('/outbound/list', { params })
      console.log('API: Response from outbound/list:', response)
      return response
    } catch (error) {
      console.error('API: Error fetching outbound list:', error)
      throw error
    }
  },

  /**
   * 获取出库单详情
   * @param {number} id - 出库单ID
   * @returns {Promise} - 返回出库单详情
   */
  getOutboundById(id) {
    return api.get(`/outbound/${id}`)
  },

  /**
   * 导入出库单
   * @param {FormData} formData - 包含Excel文件的FormData
   * @returns {Promise} - 返回导入结果
   */
  importOutbounds(formData) {
    console.log('Importing outbounds with FormData:', formData)

    // 检查 FormData 内容
    for (let pair of formData.entries()) {
      console.log('FormData entry:', pair[0], pair[1])
    }

    // 添加超时时间
    return api.post('/outbound/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000  // 增加超时时间到 60 秒
    })
      .catch(error => {
        console.error('Import API error details:', error.response || error)
        throw error
      })
  },

  /**
   * 完成出库操作
   * @param {number} id - 出库单ID
   * @returns {Promise} - 返回完成结果
   */
  completeOutbound(id) {
    return api.post(`/outbound/complete/${id}`)
  },

  /**
   * 删除出库单
   * @param {number} id - 出库单ID
   * @param {string} reason - 删除原因
   * @returns {Promise} - 返回删除结果
   */
  deleteOutbound(id, reason) {
    return api.delete(`/outbound/${id}`, {
      params: { reason: reason || '' }
    })
  },

  /**
   * 批量删除出库单
   * @param {Array<number>} ids - 出库单ID数组
   * @param {string} reason - 删除原因
   * @returns {Promise} - 返回删除结果
   */
  batchDeleteOutbounds(ids, reason) {
    return api.post('/outbound/batch-delete', { ids }, {
      params: { reason: reason || '' }
    })
  },

  /**
   * 获取审计记录列表
   * @param {Object} params - 查询参数
   * @returns {Promise} - 返回审计记录列表
   */
  getAuditRecords(params) {
    return api.get('/outbound/audit/records', { params })
  },

  /**
   * 获取审计记录详情
   * @param {number} id - 审计记录ID
   * @returns {Promise} - 返回审计记录详情
   */
  getAuditRecord(id) {
    return api.get(`/outbound/audit/records/${id}`)
  }
}
