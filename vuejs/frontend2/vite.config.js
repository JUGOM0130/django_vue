import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { resolve } from 'path'



export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    rollupOptions: {
      input: {
        default: resolve(__dirname, 'index.html'),
        node: resolve(__dirname, 'src/pages/nodes/index.html'),
        tree: resolve(__dirname, 'src/pages/trees/index.html')
      }
    }
  },
  server: {
    port: 3000
    ,open: true
  } 
})