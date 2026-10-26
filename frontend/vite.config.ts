import path from 'path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    // 5173 与本机其他项目(拼豆乐园)冲突：同一端口上 IPv4/IPv6 被不同进程分别绑定，
    // 浏览器访问 localhost 时命中哪个取决于解析顺序，表现为"有时能开、有时开的是别的项目"。
    // 改用 5180，彻底避开。strictPort 让端口被占时直接报错，避免静默漂移到随机端口。
    port: 5180,
    strictPort: true,
    proxy: {
      '/api':       { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/oauth2':    { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/uploads':   { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/ws':        { target: 'ws://127.0.0.1:8080',   ws: true, changeOrigin: true },
    },
  },
})
