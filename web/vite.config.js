import {defineConfig} from "vite";

export default defineConfig(({command}) => {
    return {
        base: getBase(command),
        server: {
            port: 3000,
            proxy: {
                '/api': {
                    target: 'http://api:8080',
                    changeOrigin: true,
                    rewrite: (path) => path.replace(/^\/api/, ''),
                },
            },
        }
    }
})