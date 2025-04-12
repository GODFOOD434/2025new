<template>
  <div class="report-dashboard-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据看板</span>
        </div>
      </template>
      
      <div class="dashboard-content">
        <h2>数据看板功能正在开发中...</h2>
        <p>该功能将提供以下内容：</p>
        <ul>
          <li>采购订单统计</li>
          <li>工作流处理情况</li>
          <li>库存状态分析</li>
          <li>质检通过率</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'ReportDashboard'
}
</script>

<style scoped>
.report-dashboard-container {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-content {
  padding: 20px;
  text-align: center;
}

h2 {
  margin-bottom: 20px;
  color: #409EFF;
}

ul {
  display: inline-block;
  text-align: left;
  margin-top: 20px;
}

li {
  margin: 10px 0;
}
</style>
