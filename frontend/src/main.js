import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import store from './store'

// 导入自定义样式
// 用于解决 -ms-high-contrast 弃用警告
import './assets/css/forced-colors.css'
// 导入全局样式优化
import './assets/css/global.css'

const app = createApp(App)

app.use(ElementPlus)
app.use(router)
app.use(store)

app.mount('#app')
