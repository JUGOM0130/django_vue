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
  pages:{
    top:{
      entry:'src/main.js',
      template:'public/index.html',
      filename:'index.html'
    },
    tree:{
      entry:'src/entrysjs/tree.js',
      template:'public/tree.html',
      filename:'tree.html'
    }
  },

  pluginOptions: {
    vuetify: {
			// https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
		}
  }
})
