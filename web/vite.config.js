import {defineConfig} from "vite";

export default defineConfig({
    server: {
        port: 3000,
        proxy: {
            '/api': {
                target: 'http://api:5000',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, ''),
            },
        },
    },
})