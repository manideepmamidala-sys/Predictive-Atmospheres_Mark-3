import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  server: { proxy: { '/v1': process.env.PA_API_URL || loadEnv(mode, process.cwd(), 'PA_').PA_API_URL || 'http://127.0.0.1:8000' } },
  build: { sourcemap: true },
}));
