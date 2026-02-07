import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from 'tailwindcss'

<<<<<<< HEAD
// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/modules': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/ai': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
=======
// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    css: {
      postcss: {
        plugins: [tailwindcss()],
      },
    },
    define: {
      // Expose Supabase keys to the client. 
      // We map the non-prefixed vars (from .env or Vercel) to VITE_ prefixed ones for consistency
      // or just expose them as is if we change the client code to match.
      // Better: map them to 'import.meta.env.VITE_SUPABASE_URL'
      'import.meta.env.VITE_SUPABASE_URL': JSON.stringify(env.SUPABASE_URL || env.NEXT_PUBLIC_SUPABASE_URL),
      'import.meta.env.VITE_SUPABASE_ANON_KEY': JSON.stringify(env.SUPABASE_ANON_KEY || env.NEXT_PUBLIC_SUPABASE_ANON_KEY),
    }
  }
>>>>>>> ef33f0c (Fix production app: add core module to vercel.json, improve package structure, use Vercel env vars)
})
