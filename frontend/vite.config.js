import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/check-db-connection': 'http://localhost:8000',
      '/demotable': 'http://localhost:8000',
      '/initiate-demotable': 'http://localhost:8000',
      '/insert-demotable': 'http://localhost:8000',
      '/update-name-demotable': 'http://localhost:8000',
      '/count-demotable': 'http://localhost:8000'
    }
  }
});
