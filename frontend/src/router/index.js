import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// 路由懒加载
const Login = () => import('../views/Login.vue')
const Layout = () => import('../views/Layout.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const PurchaseOrderList = () => import('../views/purchase/OrderList.vue')
const PurchaseOrderImport = () => import('../views/purchase/OrderImport.vue')
const PurchaseOrderDetail = () => import('../views/purchase/OrderDetail.vue')
const WorkflowTasks = () => import('../views/workflow/Tasks.vue')
const WorkflowDetail = () => import('../views/workflow/Detail.vue')
const ConfirmationList = () => import('../views/confirmation/List.vue')
const ConfirmationDetail = () => import('../views/confirmation/Detail.vue')
const OutboundList = () => import('../views/outbound/List.vue')
const OutboundImport = () => import('../views/outbound/Import.vue')
const OutboundDetail = () => import('../views/outbound/Detail.vue')
const OutboundAuditList = () => import('../views/outbound/AuditList.vue')
const OutboundAuditDetail = () => import('../views/outbound/AuditDetail.vue')
const InventoryList = () => import('../views/inventory/List.vue')
const InventoryDetail = () => import('../views/inventory/Detail.vue')
const ReportDashboard = () => import('../views/report/Dashboard.vue')
const UserProfile = () => import('../views/user/Profile.vue')
const UserManagement = () => import('../views/user/Management.vue')
const NotFound = () => import('../views/NotFound.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '首页' }
      },
      {
        path: 'purchase',
        name: 'PurchaseOrderList',
        component: PurchaseOrderList,
        meta: { title: '采购订单列表' }
      },
      {
        path: 'purchase/import',
        name: 'PurchaseOrderImport',
        component: PurchaseOrderImport,
        meta: { title: '导入采购订单' }
      },
      {
        path: 'purchase/:id',
        name: 'PurchaseOrderDetail',
        component: PurchaseOrderDetail,
        meta: { title: '采购订单详情' }
      },
      {
        path: 'workflow/tasks',
        name: 'WorkflowTasks',
        component: WorkflowTasks,
        meta: { title: '我的任务' }
      },
      {
        path: 'workflow/:id',
        name: 'WorkflowDetail',
        component: WorkflowDetail,
        meta: { title: '工作流详情' }
      },
      {
        path: 'confirmation',
        name: 'ConfirmationList',
        component: ConfirmationList,
        meta: { title: '确认单列表' }
      },
      {
        path: 'confirmation/:id',
        name: 'ConfirmationDetail',
        component: ConfirmationDetail,
        meta: { title: '确认单详情' }
      },
      {
        path: 'outbound',
        name: 'OutboundList',
        component: OutboundList,
        meta: { title: '出库单列表' }
      },
      {
        path: 'outbound/import',
        name: 'OutboundImport',
        component: OutboundImport,
        meta: { title: '导入出库单' }
      },
      {
        path: 'outbound/audit/list',
        name: 'OutboundAuditList',
        component: OutboundAuditList,
        meta: { title: '出库单删除记录' }
      },
      {
        path: 'outbound/audit/detail/:id',
        name: 'OutboundAuditDetail',
        component: OutboundAuditDetail,
        meta: { title: '删除记录详情' }
      },
      {
        path: 'outbound/:id',
        name: 'OutboundDetail',
        component: OutboundDetail,
        meta: { title: '出库单详情' }
      },
      {
        path: 'inventory',
        name: 'InventoryList',
        component: InventoryList,
        meta: { title: '库存列表' }
      },
      {
        path: 'inventory/:id',
        name: 'InventoryDetail',
        component: InventoryDetail,
        meta: { title: '库存详情' }
      },
      {
        path: 'report',
        name: 'ReportDashboard',
        component: ReportDashboard,
        meta: { title: '报表看板' }
      },
      {
        path: 'user/profile',
        name: 'UserProfile',
        component: UserProfile,
        meta: { title: '个人信息' }
      },
      {
        path: 'user/management',
        name: 'UserManagement',
        component: UserManagement,
        meta: { title: '用户管理', requiresAdmin: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 仓储工作流系统`
  }

  // 检查是否需要登录
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const isLoggedIn = store.getters['auth/isLoggedIn']
  const isAdmin = store.getters['auth/isAdmin']

  if (requiresAuth && !isLoggedIn) {
    next('/login')
  } else if (requiresAdmin && !isAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router
