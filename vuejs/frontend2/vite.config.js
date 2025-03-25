import { defineConfig, loadEnv } from 'vite' // loadEnvを追加
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { resolve } from 'path'

// default exportを関数形式に変更
export default defineConfig(({ command, mode }) => {
  // 環境変数を読み込む
  const env = loadEnv(mode, process.cwd(), '')

  // デバッグ用のログ出力
  console.log('Build Mode:', mode)
  console.log('Environment Variables:', env)

  return {
    plugins: [vue()],
    base: '/',
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    build: {
      outDir: '../../dist',
      assetsDir: 'assets',
      emptyOutDir: true,
      rollupOptions: {
        input: {
          default: resolve(__dirname, 'index.html'),
          node: resolve(__dirname, 'src/pages/nodes/index.html'),
          tree: resolve(__dirname, 'src/pages/trees/index.html')
        }
      }
    },
    server: {
      port: 3000,
      open: true
    },
    // 必要に応じて環境変数関連の設定を追加
    define: {
      __VUE_ENV__: JSON.stringify(env)
    }
  }
})