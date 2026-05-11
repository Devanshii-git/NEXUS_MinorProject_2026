import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'

export default defineConfig({
  plugins: [react(), basicSsl()],
  base: './',
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/atlassian': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
        cookieDomainRewrite: 'localhost',
        cookiePathRewrite: '/',
      },
      '/slack': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
        cookieDomainRewrite: 'localhost',
        cookiePathRewrite: '/',
      },
      '/user': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
        cookieDomainRewrite: 'localhost',
        cookiePathRewrite: '/',
      },
      '/logged': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
        cookieDomainRewrite: 'localhost',
        cookiePathRewrite: '/',
      },
      '/oauth2': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
        cookieDomainRewrite: 'localhost',
        cookiePathRewrite: '/',
      },
      '/login': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
        cookieDomainRewrite: 'localhost',
        cookiePathRewrite: '/',
      },
      '/logout': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
        cookieDomainRewrite: 'localhost',
        cookiePathRewrite: '/',
      },
      '/tests': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
        cookieDomainRewrite: 'localhost',
        cookiePathRewrite: '/',
      },
      '/ai': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
        cookieDomainRewrite: 'localhost',
        cookiePathRewrite: '/',
      },
    },
  },
  build: {
    outDir: 'dist',
  },
})
