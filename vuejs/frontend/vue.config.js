const { defineConfig } = require('@vue/cli-service')
const path = require('path');
module.exports = defineConfig({
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',
  outputDir: "../../avail/entrypoint/dist/",//staticDirとして設定
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
    /*
    top:{
      entry:'src/main.js',
      template:'public/index.html', //ここをfilenameと合わせないとエラーする
      filename:process.env.NODE_ENV === 'production'
      ? path.resolve(__dirname, '../../avail/entrypoint/templates/index.html')
      : "index.html", //pagesブロックにindex.htmlがあるとBASEURLでアクセスした時に一番に開かれる
    },*/
    login:{
      entry:'src/entrysjs/login.js',
      template:'public/index.html',
      title:"login",
      filename:process.env.NODE_ENV === 'production'
      ? path.resolve(__dirname, '../../avail/entrypoint/templates/login.html')
      : "index.html",
    },
    tree:{
      entry:'src/entrysjs/tree.js',
      template:'public/tree.html',
      filename:process.env.NODE_ENV === 'production'
      ? path.resolve(__dirname, '../../avail/entrypoint/templates/tree.html')
      : "tree.html",
    }
  },

  pluginOptions: {
    vuetify: {
			// https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
		}
  }
})
