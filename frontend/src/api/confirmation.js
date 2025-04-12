import api from './index'

export default {
  /**
   * 获取确认单列表
   * @param {number} page - 页码
   * @param {number} size - 每页数量
   * @param {Object} filters - 过滤条件
   * @returns {Promise} - 返回确认单列表
   */
  getConfirmations(page = 1, size = 10, filters = {}) {
    // 处理日期参数，确保发送正确的格式
    const params = {
      page,
      size
    }

    // 处理过滤条件
    if (filters.order_no) params.order_no = filters.order_no
    if (filters.confirmation_no) params.confirmation_no = filters.confirmation_no

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

    console.log('Sending params to confirmation/list:', params)

    return api.get('/confirmation/list', { params })
  },

  /**
   * 生成确认单
   * @param {string} orderNo - 采购订单号
   * @returns {Promise} - 返回生成结果
   */
  generateConfirmation(orderNo) {
    return api.post('/confirmation/generate', { order_no: orderNo })
  },

  /**
   * 打印确认单
   * @param {number} id - 确认单ID
   * @returns {Promise} - 返回打印结果
   */
  printConfirmation(id) {
    return api.post(`/confirmation/${id}/print`)
  },

  /**
   * 获取确认单PDF
   * @param {number} id - 确认单ID
   * @returns {Promise} - 返回PDF URL
   */
  getConfirmationPdf(id) {
    return api.get(`/confirmation/${id}/pdf`)
  }
}
