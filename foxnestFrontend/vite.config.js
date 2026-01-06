import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
  server: {
    host: '0.0.0.0',   // listen on all interfaces
    port: 5173,        // preferred port
    strictPort: false, // allow fallback if 5173 is in use
  },
})
