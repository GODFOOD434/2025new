import api from './index'

export default {
  /**
   * 获取待办任务列表
   * @param {number} page - 页码
   * @param {number} size - 每页数量
   * @param {Object} filters - 过滤条件
   * @returns {Promise} - 返回任务列表
   */
  getTasks(page = 1, size = 10, filters = {}) {
    return api.get('/workflow/tasks/todo', {
      params: {
        page,
        size,
        ...filters
      }
    })
  },
  
  /**
   * 发起工作流
   * @param {Object} data - 工作流数据
   * @param {string} data.order_no - 采购订单号
   * @param {string} data.workflow_type - 工作流类型
   * @param {string} data.delivery_type - 交付类型
   * @returns {Promise} - 返回工作流实例
   */
  startWorkflow(data) {
    return api.post('/workflow/start', data)
  },
  
  /**
   * 完成任务
   * @param {string} taskId - 任务ID
   * @param {Object} data - 任务完成数据
   * @param {boolean} data.approved - 是否批准
   * @param {string} data.comment - 评论
   * @returns {Promise} - 返回任务完成结果
   */
  completeTask(taskId, data) {
    return api.post(`/workflow/task/${taskId}/complete`, data)
  }
}
