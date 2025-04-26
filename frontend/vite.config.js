import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/scan': 'http://127.0.0.1:5000',
      '/scan_with_score': 'http://127.0.0.1:5000',
      '/traffic': 'http://127.0.0.1:5000',
      '/report': 'http://127.0.0.1:5000',
      '/agent': 'http://127.0.0.1:5000',
      '/auth': 'http://127.0.0.1:5000'
    }
  }
});
