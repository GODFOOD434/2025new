import api from './index'

export default {
  /**
   * 获取采购订单列表
   * @param {number} page - 页码
   * @param {number} size - 每页数量
   * @param {Object} filters - 过滤条件
   * @returns {Promise} - 返回采购订单列表
   */
  getOrders(page = 1, size = 10, filters = {}) {
    return api.get('/purchase/list', {
      params: {
        page,
        size,
        ...filters
      }
    })
  },

  /**
   * 获取采购订单详情
   * @param {number} id - 采购订单ID
   * @returns {Promise} - 返回采购订单详情
   */
  getOrderById(id) {
    return api.get(`/purchase/${id}`)
  },

  /**
   * 导入采购订单
   * @param {FormData} formData - 包含Excel文件的FormData
   * @returns {Promise} - 返回导入结果
   */
  importOrders(formData) {
    console.log('Importing purchase orders with FormData:', formData)

    // 检查 FormData 内容
    for (let pair of formData.entries()) {
      console.log('FormData entry:', pair[0], pair[1])
    }

    // 添加超时时间和错误处理
    return api.post('/purchase/import', formData, {
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
   * 更新采购订单
   * @param {number} id - 采购订单ID
   * @param {Object} data - 更新数据
   * @returns {Promise} - 返回更新结果
   */
  updateOrder(id, data) {
    return api.put(`/purchase/${id}`, data)
  },

  /**
   * 获取所有用户单位
   * @returns {Promise} - 返回用户单位列表
   */
  getUserUnits() {
    return api.get('/purchase/user-units')
  }
}
