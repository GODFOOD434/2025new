<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <!-- 欢迎卡片 -->
      <el-col :span="24">
        <el-card class="welcome-card">
          <div class="welcome-info">
            <h2>欢迎使用仓储工作流系统</h2>
            <p>{{ greeting }}，{{ currentUser ? (currentUser.full_name || currentUser.username) : '用户' }}</p>
          </div>
          <div class="welcome-actions">
            <el-button type="primary" @click="$router.push('/workflow/tasks')">
              我的任务 <el-badge v-if="todoCount > 0" :value="todoCount" />
            </el-button>
            <el-button @click="$router.push('/purchase/import')">导入采购订单</el-button>
            <el-button @click="$router.push('/outbound/import')">导入出库单</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-row">
      <!-- 统计卡片 -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon">
            <el-icon><icon-document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-title">采购订单</div>
            <div class="stat-value">{{ stats.orderCount }}</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon">
            <el-icon><icon-s-order /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-title">待处理工作流</div>
            <div class="stat-value">{{ stats.pendingWorkflowCount }}</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon">
            <el-icon><icon-s-goods /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-title">库存价值</div>
            <div class="stat-value">{{ formatCurrency(stats.inventoryValue) }}</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon">
            <el-icon><icon-s-data /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-title">质检通过率</div>
            <div class="stat-value">{{ formatPercent(stats.qualityPassRate) }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-row">
      <!-- 待办任务 -->
      <el-col :span="12">
        <el-card class="task-card">
          <template #header>
            <div class="card-header">
              <span>待办任务</span>
              <el-button type="text" @click="$router.push('/workflow/tasks')">查看全部</el-button>
            </div>
          </template>
          <div v-if="tasks.length === 0" class="empty-data">
            暂无待办任务
          </div>
          <el-table v-else :data="tasks" style="width: 100%">
            <el-table-column prop="taskName" label="任务名称" />
            <el-table-column prop="businessKey" label="业务单号" width="180" />
            <el-table-column prop="createTime" label="创建时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.createTime) }}
              </template>
            </el-table-column>
            <el-table-column fixed="right" label="操作" width="120">
              <template #default="scope">
                <el-button type="text" @click="handleTask(scope.row)">处理</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 系统通知 -->
      <el-col :span="12">
        <el-card class="notification-card">
          <template #header>
            <div class="card-header">
              <span>系统通知</span>
              <el-button type="text" @click="markAllRead">全部标记为已读</el-button>
            </div>
          </template>
          <div v-if="notifications.length === 0" class="empty-data">
            暂无系统通知
          </div>
          <div v-else class="notification-list">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              class="notification-item"
              :class="{ 'is-read': notification.is_read }"
              @click="viewNotification(notification)"
            >
              <div class="notification-content">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-body">{{ notification.content }}</div>
              </div>
              <div class="notification-time">{{ formatTime(notification.send_time) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-row">
      <!-- 订单趋势图 -->
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>订单趋势</span>
              <el-radio-group v-model="timeRange" size="small" @change="fetchDashboardData">
                <el-radio-button label="TODAY">今日</el-radio-button>
                <el-radio-button label="WEEK">本周</el-radio-button>
                <el-radio-button label="MONTH">本月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container">
            <!-- 这里可以使用ECharts等图表库 -->
            <div v-if="!stats.orderTrend || stats.orderTrend.length === 0" class="empty-data">
              暂无数据
            </div>
            <div v-else class="chart-placeholder">
              订单趋势图表
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import {
  Document as IconDocument,
  Tickets as IconSOrder,
  Goods as IconSGoods,
  DataAnalysis as IconSData
} from '@element-plus/icons-vue'

export default {
  name: 'Dashboard',

  components: {
    IconDocument,
    IconSOrder,
    IconSGoods,
    IconSData
  },

  setup() {
    const store = useStore()
    const router = useRouter()

    // 时间范围
    const timeRange = ref('MONTH')

    // 获取当前用户
    const currentUser = computed(() => store.getters['auth/currentUser'])

    // 获取问候语
    const greeting = computed(() => {
      const hour = new Date().getHours()
      if (hour < 6) return '凌晨好'
      if (hour < 9) return '早上好'
      if (hour < 12) return '上午好'
      if (hour < 14) return '中午好'
      if (hour < 17) return '下午好'
      if (hour < 19) return '傍晚好'
      return '晚上好'
    })

    // 获取统计数据
    const stats = ref({
      orderCount: 0,
      pendingWorkflowCount: 0,
      inventoryValue: 0,
      qualityPassRate: 0,
      orderTrend: []
    })

    // 获取待办任务
    const tasks = ref([])
    const todoCount = computed(() => tasks.value.length)

    // 获取通知
    const notifications = computed(() => store.getters['notification/notifications'])

    // 获取看板数据
    const fetchDashboardData = async () => {
      try {
        const data = await store.dispatch('report/getLeadershipDashboard', timeRange.value)
        stats.value = data
      } catch (error) {
        console.error('获取看板数据失败:', error)
      }
    }

    // 获取待办任务
    const fetchTasks = async () => {
      try {
        const result = await store.dispatch('workflow/getTasks', { page: 1, size: 5 })
        tasks.value = result
      } catch (error) {
        console.error('获取待办任务失败:', error)
      }
    }

    // 处理任务
    const handleTask = (task) => {
      router.push(`/workflow/${task.workflowInstanceId}`)
    }

    // 查看通知
    const viewNotification = (notification) => {
      if (!notification.is_read) {
        store.dispatch('notification/markAsRead', notification.id)
      }
      // 这里可以打开通知详情
    }

    // 全部标记为已读
    const markAllRead = () => {
      store.dispatch('notification/markAllAsRead')
    }

    // 格式化货币
    const formatCurrency = (value) => {
      if (!value) return '¥0.00'
      return '¥' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
    }

    // 格式化百分比
    const formatPercent = (value) => {
      if (!value && value !== 0) return '0%'
      return (value * 100).toFixed(2) + '%'
    }

    // 格式化日期
    const formatDate = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleDateString()
    }

    // 格式化时间
    const formatTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString()
    }

    // 组件挂载时获取数据
    onMounted(() => {
      fetchDashboardData()
      fetchTasks()
      store.dispatch('notification/getNotifications')
    })

    return {
      timeRange,
      currentUser,
      greeting,
      stats,
      tasks,
      todoCount,
      notifications,
      fetchDashboardData,
      handleTask,
      viewNotification,
      markAllRead,
      formatCurrency,
      formatPercent,
      formatDate,
      formatTime
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px 0;
}

.dashboard-row {
  margin-bottom: 20px;
}

.welcome-card {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-info h2 {
  margin: 0 0 10px;
  font-size: 24px;
  color: #303133;
}

.welcome-info p {
  margin: 0;
  font-size: 16px;
  color: #606266;
}

.welcome-actions {
  display: flex;
  gap: 10px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  font-size: 48px;
  color: #409EFF;
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  color: #303133;
  font-weight: bold;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-data {
  text-align: center;
  padding: 30px 0;
  color: #909399;
  font-size: 14px;
}

.notification-list {
  max-height: 300px;
  overflow-y: auto;
}

.notification-item {
  padding: 10px 0;
  border-bottom: 1px solid #EBEEF5;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background-color: #F5F7FA;
}

.notification-item.is-read {
  opacity: 0.6;
}

.notification-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 5px;
}

.notification-body {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}

.chart-container {
  height: 300px;
}

.chart-placeholder {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #909399;
  font-size: 16px;
  background-color: #F5F7FA;
  border-radius: 4px;
}
</style>
