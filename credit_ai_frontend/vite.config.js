import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

function internalToken() {
  if (process.env.INTERNAL_TOKEN) return process.env.INTERNAL_TOKEN
  try {
    const text = fs.readFileSync(path.resolve(__dirname, '../.env'), 'utf8')
    for (const line of text.split(/\r?\n/)) {
      const match = line.match(/^INTERNAL_TOKEN=(.*)$/)
      if (match) return match[1].trim().replace(/^["']|["']$/g, '')
    }
  } catch {
    // No repo-root .env during some CI builds.
  }
  return ''
}

const INTERNAL_TOKEN = internalToken()

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api/chat': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api\/chat/, '/chat'),
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes) => {
            if (proxyRes.headers['content-type']?.includes('text/plain')) {
              proxyRes.headers['cache-control'] = 'no-cache'
              proxyRes.headers['x-accel-buffering'] = 'no'
            }
          })
        },
      },
      '/api/search': {
        target: 'http://127.0.0.1:3000',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api\/search/, ''),
        configure: (proxy) => {
          if (!INTERNAL_TOKEN) return
          proxy.on('proxyReq', (proxyReq) => {
            proxyReq.setHeader('X-Internal-Token', INTERNAL_TOKEN)
          })
        },
      },
      '/api/chat_history': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api\/chat_history/, '/chat_history'),
      },
      '/api/auth': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api\/auth/, '/auth'),
      },
      '/api/admin': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api\/admin/, '/admin'),
      },
    },
  },
})
