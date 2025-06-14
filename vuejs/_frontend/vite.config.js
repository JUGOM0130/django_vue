import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],

  base: '/',  // 基本パスの確認（"/"で問題ないはず）

  //root: './public',  // プロジェクトのルートディレクトリを指定
  root: 'src',

  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),  // '@'を'src'ディレクトリにマッピング
    }
  },

  build: {
    outDir: '../../avail/entrypoint/dist',  // 出力先
    //outDir: 'dist',  // 出力先
    assetsDir: 'static',  // アセットディレクトリ
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/main.js'),  // main.jsのエントリーポイント
        login: path.resolve(__dirname, 'src/entrysjs/login.js'),
        tree: path.resolve(__dirname, 'src/entrysjs/tree.js')
      }
    }
  },

  server: {
    host: 'localhost',
    port: 8080,
    hot: true,  // ホットリロード
  },
});
