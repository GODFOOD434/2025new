import api from './index'

export default {
  /**
   * 获取领导层看板数据
   * @param {string} timeRange - 时间范围（TODAY, WEEK, MONTH）
   * @returns {Promise} - 返回看板数据
   */
  getLeadershipDashboard(timeRange = 'MONTH') {
    return api.get('/reports/dashboard/leadership', {
      params: { time_range: timeRange }
    })
  },
  
  /**
   * 获取运营看板数据
   * @returns {Promise} - 返回看板数据
   */
  getOperationDashboard() {
    return api.get('/reports/dashboard/operation')
  }
}
