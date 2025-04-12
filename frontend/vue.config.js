module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api/v1'
        }
      }
    }
  },
  transpileDependencies: [
    'vuex',
    'vue-router',
    'element-plus'
  ]
}
