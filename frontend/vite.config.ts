import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// VITE_PROXY_TARGET é lida em tempo de execução do servidor Node (não do browser).
// - Local:  http://localhost:8000  (padrão)
// - Docker: http://backend:8000   (definido no docker-compose)
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: process.env['VITE_PROXY_TARGET'] ?? 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
