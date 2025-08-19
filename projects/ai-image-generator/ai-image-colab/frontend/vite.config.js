import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  base: '/static/apps/ai-image-colab/',
  plugins: [react()],
})
