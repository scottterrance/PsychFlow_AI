import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Bind explicitly to IPv4 127.0.0.1. On Windows, Vite's default can bind
    // only to IPv6 ([::1]), which breaks `http://localhost:5173` when the OS
    // resolves localhost to IPv4 first. Forcing 127.0.0.1 is reliable.
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      // Use 127.0.0.1 (not localhost) for the same IPv4/IPv6 reason.
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
