import api from './index'

export default {
  /**
   * 获取库存列表
   * @param {number} page - 页码
   * @param {number} size - 每页数量
   * @param {Object} filters - 过滤条件
   * @returns {Promise} - 返回库存列表
   */
  getInventories(page = 1, size = 10, filters = {}) {
    return api.get('/inventory/list', {
      params: {
        page,
        size,
        ...filters
      }
    })
  },

  /**
   * 获取库存详情
   * @param {number} id - 库存ID
   * @returns {Promise} - 返回库存详情
   */
  getInventoryById(id) {
    return api.get(`/inventory/${id}`)
  },

  /**
   * 创建库存
   * @param {Object} data - 库存数据
   * @returns {Promise} - 返回创建结果
   */
  createInventory(data) {
    return api.post('/inventory', data)
  },

  /**
   * 更新库存
   * @param {number} id - 库存ID
   * @param {Object} data - 更新数据
   * @returns {Promise} - 返回更新结果
   */
  updateInventory(id, data) {
    return api.put(`/inventory/${id}`, data)
  },

  /**
   * 获取库存事务列表
   * @param {number} page - 页码
   * @param {number} size - 每页数量
   * @param {Object} filters - 过滤条件
   * @returns {Promise} - 返回库存事务列表
   */
  getTransactions(page = 1, size = 10, filters = {}) {
    return api.get('/inventory/transactions', {
      params: {
        page,
        size,
        ...filters
      }
    })
  }
}
