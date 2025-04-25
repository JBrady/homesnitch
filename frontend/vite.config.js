import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/scan': 'http://localhost:5000',
      '/scan_with_score': 'http://localhost:5000',
      '/traffic': 'http://localhost:5000'
    }
  }
});
