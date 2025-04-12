<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>页面不存在</h2>
      <p>抱歉，您访问的页面不存在或已被移除。</p>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
}

.not-found-content {
  max-width: 500px;
}

.not-found h1 {
  font-size: 120px;
  margin: 0;
  color: #409EFF;
}

.not-found h2 {
  font-size: 30px;
  margin: 0 0 20px;
  color: #303133;
}

.not-found p {
  font-size: 16px;
  margin: 0 0 30px;
  color: #606266;
}
</style>
