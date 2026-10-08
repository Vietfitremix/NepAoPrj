import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { cpSync, existsSync, readFileSync, statSync } from 'node:fs';
import { join, normalize, resolve } from 'node:path';

// Bộ ảnh người mẫu giấy của Nếp Áo nằm ở src/assets/figure (công cụ trong tools/ ghi vào đó) — phục vụ ở /figure/*, build thì chép vào dist/figure.
const FIGURE = resolve(__dirname, 'src/assets/figure');
function figureAssets(): Plugin {
  return {
    name: 'nepao-figure',
    configureServer(server) {
      server.middlewares.use('/figure', (req, res, next) => {
        const file = normalize(join(FIGURE, decodeURIComponent((req.url || '/').split('?')[0])));
        if (!file.startsWith(FIGURE) || !existsSync(file) || !statSync(file).isFile()) return next();
        res.setHeader('Content-Type', file.endsWith('.svg') ? 'image/svg+xml' : 'application/octet-stream');
        res.end(readFileSync(file));
      });
    },
    closeBundle() {
      if (existsSync(FIGURE)) cpSync(FIGURE, resolve(__dirname, 'dist/figure'), { recursive: true });
    },
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), figureAssets()],
  server: { proxy: { '/api': { target: 'http://localhost:8080', changeOrigin: true }, '/ai': { target: 'http://localhost:8080', changeOrigin: true } } },
});
