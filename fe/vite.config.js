/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({
    plugins: [react(), tailwindcss()],
    resolve: {
        // @/ = src/. Las importaciones ENTRE capas o features usan el alias;
        // dentro de una misma feature se usan rutas relativas (ver src/README.md).
        alias: { "@": "/src" },
    },
    server: {
        port: 5173,
    },
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: './src/test/setup.ts',
    },
});
