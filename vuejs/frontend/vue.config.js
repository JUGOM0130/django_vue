const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  publicPath: "/",
  outputDir: "../../djang-env/mainproject/dist/",
  assetsDir:  "static",
  indexPath: "../templates/index.html",
  transpileDependencies: true,
  devServer: {
    host: "localhost",
    hot: "only",
    proxy: {
      "^/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
})
