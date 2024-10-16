import {defineConfig} from "vite";

export default defineConfig(({command}) => {
    return {
        server: {
            port: 3000,
            proxy: {
                '/api': {
                    target: 'http://localhost:8080',
                    changeOrigin: true,
                    rewrite: (path) => path.replace(/^\/api/, ''),
                },
            },
        }
    }
})