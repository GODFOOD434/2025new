<template>
  <div class="app-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="200px">
        <div class="logo">
          <h2>仓储工作流系统</h2>
        </div>

        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          :collapse="isCollapse"
          router
        >
          <el-menu-item index="/">
            <el-icon><icon-menu /></el-icon>
            <span>首页</span>
          </el-menu-item>

          <el-sub-menu index="/purchase">
            <template #title>
              <el-icon><icon-document /></el-icon>
              <span>采购订单管理</span>
            </template>
            <el-menu-item index="/purchase">采购订单列表</el-menu-item>
            <el-menu-item index="/purchase/import">导入采购订单</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/workflow/tasks">
            <el-icon><icon-s-order /></el-icon>
            <span>我的任务</span>
          </el-menu-item>

          <el-menu-item index="/confirmation">
            <el-icon><icon-s-claim /></el-icon>
            <span>确认单管理</span>
          </el-menu-item>

          <el-sub-menu index="/outbound">
            <template #title>
              <el-icon><icon-s-cooperation /></el-icon>
              <span>出库管理</span>
            </template>
            <el-menu-item index="/outbound">出库单列表</el-menu-item>
            <el-menu-item index="/outbound/import">导入出库单</el-menu-item>
            <el-menu-item index="/outbound/audit/list">删除记录</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/inventory">
            <el-icon><icon-s-goods /></el-icon>
            <span>库存管理</span>
          </el-menu-item>

          <el-menu-item index="/report">
            <el-icon><icon-s-data /></el-icon>
            <span>报表看板</span>
          </el-menu-item>

          <el-sub-menu index="/user">
            <template #title>
              <el-icon><icon-user /></el-icon>
              <span>用户管理</span>
            </template>
            <el-menu-item index="/user/profile">个人信息</el-menu-item>
            <el-menu-item v-if="isAdmin" index="/user/management">用户管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <!-- 头部 -->
        <el-header>
          <div class="header-left">
            <el-button
              type="text"
              @click="toggleSidebar"
            >
              <el-icon><icon-fold /></el-icon>
            </el-button>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="currentRoute.meta.title">{{ currentRoute.meta.title }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <div class="header-right">
            <!-- 通知 -->
            <el-dropdown trigger="click" @command="handleNotification">
              <el-badge :value="unreadCount" :max="99" class="notification-badge">
                <el-button type="text">
                  <el-icon><icon-bell /></el-icon>
                </el-button>
              </el-badge>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="notifications.length === 0" disabled>
                    暂无通知
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-for="notification in notifications.slice(0, 5)"
                    :key="notification.id"
                    :command="{ type: 'view', id: notification.id }"
                  >
                    <div class="notification-item">
                      <div class="notification-title">{{ notification.title }}</div>
                      <div class="notification-time">{{ formatTime(notification.send_time) }}</div>
                    </div>
                  </el-dropdown-item>
                  <el-dropdown-item divided command="viewAll">
                    查看全部通知
                  </el-dropdown-item>
                  <el-dropdown-item command="readAll">
                    全部标记为已读
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <!-- 用户菜单 -->
            <el-dropdown trigger="click" @command="handleCommand">
              <div class="user-info">
                <span>{{ currentUser ? (currentUser.full_name || currentUser.username) : '用户' }}</span>
                <el-icon><icon-caret-bottom /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 内容区 -->
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  Menu as IconMenu,
  Document as IconDocument,
  Setting as IconSetting,
  User as IconUser,
  Bell as IconBell,
  CaretBottom as IconCaretBottom,
  Fold as IconFold,
  Expand as IconExpand,
  Tickets as IconSOrder,
  Ticket as IconSClaim,
  Connection as IconSCooperation,
  Goods as IconSGoods,
  DataAnalysis as IconSData
} from '@element-plus/icons-vue'

export default {
  name: 'Layout',

  components: {
    IconMenu,
    IconDocument,
    IconSetting,
    IconUser,
    IconBell,
    IconCaretBottom,
    IconFold,
    IconExpand,
    IconSOrder,
    IconSClaim,
    IconSCooperation,
    IconSGoods,
    IconSData
  },

  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()

    const isCollapse = ref(false)

    // 获取当前用户
    const currentUser = computed(() => store.getters['auth/currentUser'])

    // 判断是否是管理员
    const isAdmin = computed(() => store.getters['auth/isAdmin'])

    // 获取当前路由
    const currentRoute = computed(() => route)

    // 获取活动菜单
    const activeMenu = computed(() => route.path)

    // 获取通知
    const notifications = computed(() => store.getters['notification/notifications'])
    const unreadCount = computed(() => store.getters['notification/unreadCount'])

    // 切换侧边栏
    const toggleSidebar = () => {
      isCollapse.value = !isCollapse.value
    }

    // 处理用户菜单命令
    const handleCommand = (command) => {
      if (command === 'logout') {
        ElMessageBox.confirm('确定要退出登录吗?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          store.dispatch('auth/logout')
          router.push('/login')
        }).catch(() => {})
      } else if (command === 'profile') {
        router.push('/user/profile')
      }
    }

    // 处理通知命令
    const handleNotification = (command) => {
      if (command === 'viewAll') {
        // 查看全部通知
        // 这里可以跳转到通知页面或打开通知抽屉
      } else if (command === 'readAll') {
        // 全部标记为已读
        store.dispatch('notification/markAllAsRead')
      } else if (command.type === 'view') {
        // 查看单个通知
        store.dispatch('notification/markAsRead', command.id)
        // 这里可以打开通知详情
      }
    }

    // 格式化时间
    const formatTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString()
    }

    // 组件挂载时获取通知
    onMounted(() => {
      store.dispatch('notification/getNotifications')
    })

    return {
      isCollapse,
      currentUser,
      isAdmin,
      currentRoute,
      activeMenu,
      notifications,
      unreadCount,
      toggleSidebar,
      handleCommand,
      handleNotification,
      formatTime
    }
  }
}
</script>

<style scoped>
.app-container {
  height: 100%;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: #304156;
  color: #bfcbd9;
  height: 100%;
  overflow-x: hidden;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background-color: #263445;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.el-menu-vertical {
  border-right: none;
}

.el-header {
  background-color: #fff;
  color: #333;
  line-height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-left: 20px;
}

.user-info span {
  margin-right: 5px;
}

.notification-badge {
  margin-right: 20px;
}

.notification-item {
  padding: 5px 0;
}

.notification-title {
  font-size: 14px;
  color: #303133;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}

.el-main {
  background-color: #f0f2f5;
  padding: 12px;
  overflow-y: auto;
}
</style>
