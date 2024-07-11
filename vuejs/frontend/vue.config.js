const { defineConfig } = require('@vue/cli-service')
const path = require('path');
module.exports = defineConfig({
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',
  outputDir: "../../avail/pdm/dist/",//staticDirとして設定
  assetsDir:  "static",
  indexPath: "../templates/index.html",
  transpileDependencies: true,
  devServer: {
    host: "localhost",
    port: 8080,
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
      filename:process.env.NODE_ENV === 'production'
      ? path.resolve(__dirname, '../../avail/pdm/templates/index.html')
      : "index.html",
    },
    tree:{
      entry:'src/entrysjs/tree.js',
      template:'public/tree.html',
      filename:process.env.NODE_ENV === 'production'
      ? path.resolve(__dirname, '../../avail/pdm/templates/tree.html')
      : "tree.html",
    }
  },

  pluginOptions: {
    vuetify: {
			// https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
		}
  }
})
