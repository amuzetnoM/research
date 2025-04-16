import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api/metrics': {
        target: 'http://localhost:9090',
        changeOrigin: true,
        secure: false,
      },
      '/api/container1': {
        target: 'http://localhost:8888',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/container1/, '/api'),
        secure: false,
      },
      '/api/container2': {
        target: 'http://localhost:8889',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/container2/, '/api'),
        secure: false,
      },
      '/api/grafana1': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/grafana1/, ''),
        secure: false,
      },
      '/api/grafana2': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/grafana2/, ''),
        secure: false,
      },
      '/prometheus': {
        target: 'http://localhost:9090',
        changeOrigin: true,
        secure: false,
      }
    },
  },
});