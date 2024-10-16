import {defineConfig} from "vite";

function getBase(command) {
    return command === 'build' ? '/edu-graph/' : '/';
}

export default defineConfig(({command}) => {
    return {
        base: getBase(command),
        server: {
            port: 3000,
            proxy: {
                '/api': {
                    target: 'http://api:5000',
                    changeOrigin: true,
                    rewrite: (path) => path.replace(/^\/api/, ''),
                },
            },
        }
    }
})