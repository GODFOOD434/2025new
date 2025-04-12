import api from './index'

export default {
  /**
   * 获取通知列表
   * @param {boolean} isRead - 是否已读
   * @param {string} type - 通知类型
   * @returns {Promise} - 返回通知列表
   */
  getNotifications(isRead = null, type = null) {
    const params = {}
    if (isRead !== null) params.is_read = isRead
    if (type) params.notification_type = type
    
    return api.get('/notifications', { params })
  },
  
  /**
   * 标记通知为已读
   * @param {number} id - 通知ID
   * @returns {Promise} - 返回标记结果
   */
  markAsRead(id) {
    return api.put(`/notifications/${id}/read`)
  },
  
  /**
   * 标记所有通知为已读
   * @returns {Promise} - 返回标记结果
   */
  markAllAsRead() {
    return api.put('/notifications/read-all')
  },
  
  /**
   * 创建通知
   * @param {Object} data - 通知数据
   * @returns {Promise} - 返回创建结果
   */
  createNotification(data) {
    return api.post('/notifications', data)
  },
  
  /**
   * 删除通知
   * @param {number} id - 通知ID
   * @returns {Promise} - 返回删除结果
   */
  deleteNotification(id) {
    return api.delete(`/notifications/${id}`)
  }
}
