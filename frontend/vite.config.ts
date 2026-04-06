import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/repomind',
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
