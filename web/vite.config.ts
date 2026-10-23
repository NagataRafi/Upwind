import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import fs from 'fs';

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'serve-project-data',
      configureServer(server) {
        // Melayani folder /data langsung dari ../data di root repositori
        const dataDir = path.resolve(__dirname, '../data');
        server.middlewares.use('/data', (req, res, next) => {
          if (!req.url) return next();
          const cleanUrl = req.url.split('?')[0];
          const filePath = path.join(dataDir, cleanUrl);
          if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            if (filePath.endsWith('.json')) {
              res.setHeader('Content-Type', 'application/json');
            } else if (filePath.endsWith('.png')) {
              res.setHeader('Content-Type', 'image/png');
            }
            return fs.createReadStream(filePath).pipe(res);
          }
          next();
        });
      }
    }
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    host: true,
    fs: {
      allow: ['..', 'C:/Users/ADMIN/upwind_app/node_modules']
    }
  }
});
