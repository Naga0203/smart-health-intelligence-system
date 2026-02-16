import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'
// @ts-ignore - Importing JS plugin in TS config
import { cspPlugin } from './vite-plugin-csp.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Optional: Bundle analyzer plugin
// Install with: npm install --save-dev rollup-plugin-visualizer
let visualizerPlugin;
try {
  const { visualizer } = await import('rollup-plugin-visualizer');
  visualizerPlugin = visualizer({
    filename: './dist/stats.html',
    open: false,
    gzipSize: true,
    brotliSize: true,
  });
} catch (e) {
  console.log('Bundle visualizer not installed. Install with: npm install --save-dev rollup-plugin-visualizer');
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    visualizerPlugin,
    cspPlugin(),
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/pages': path.resolve(__dirname, './src/pages'),
      '@/services': path.resolve(__dirname, './src/services'),
      '@/stores': path.resolve(__dirname, './src/stores'),
      '@/utils': path.resolve(__dirname, './src/utils'),
      '@/types': path.resolve(__dirname, './src/types'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Enable minification
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
      },
    },
    // Optimize chunk splitting
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'mui-vendor': ['@mui/material', '@mui/icons-material'],
          'firebase-vendor': ['firebase/app', 'firebase/auth'],
          'chart-vendor': ['recharts'],
          // Store chunks
          'stores': [
            './src/stores/authStore.ts',
            './src/stores/userStore.ts',
            './src/stores/assessmentStore.ts',
            './src/stores/systemStore.ts',
            './src/stores/notificationStore.ts',
          ],
        },
      },
    },
    // Chunk size warnings
    chunkSizeWarningLimit: 1000, // 1MB
    // Source maps for production debugging
    sourcemap: true,
  },
  // Optimize dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@mui/material',
      '@mui/icons-material',
      'zustand',
      'axios',
    ],
  },
})
