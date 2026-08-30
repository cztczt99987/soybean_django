import process from 'node:process';
import { URL, fileURLToPath } from 'node:url';
import { defineConfig, loadEnv } from 'vite';
import { setupVitePlugins } from './build/plugins';
import { createViteProxy, getBuildTime } from './build/config';

export default defineConfig(configEnv => {
  const viteEnv = loadEnv(configEnv.mode, process.cwd()) as unknown as Env.ImportMeta;

  const buildTime = getBuildTime();

  const enableProxy = configEnv.command === 'serve' && !configEnv.isPreview;

  // Swagger 文档页以 iframe 嵌入 Django /api/docs/，页面内部相对引用
  // /static/（swagger-ui 资源）与 /api/schema/，需补充代理到后端域名
  const backendOrigin = new URL(viteEnv.VITE_SERVICE_BASE_URL).origin;
  const swaggerProxy: Record<string, { target: string; changeOrigin: boolean }> =
    enableProxy && viteEnv.VITE_HTTP_PROXY === 'Y'
      ? {
          '/api': { target: backendOrigin, changeOrigin: true },
          '/static': { target: backendOrigin, changeOrigin: true }
        }
      : {};

  return {
    base: viteEnv.VITE_BASE_URL,
    resolve: {
      alias: {
        '~': fileURLToPath(new URL('./', import.meta.url)),
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler',
          additionalData: `@use "@/styles/scss/global.scss" as *;`
        }
      }
    },
    plugins: setupVitePlugins(viteEnv, buildTime),
    define: {
      BUILD_TIME: JSON.stringify(buildTime)
    },
    server: {
      host: '0.0.0.0',
      port: 9527,
      open: true,
      proxy: { ...(createViteProxy(viteEnv, enableProxy) ?? {}), ...swaggerProxy }
    },
    preview: {
      port: 9725
    },
    build: {
      reportCompressedSize: false,
      sourcemap: viteEnv.VITE_SOURCE_MAP === 'Y',
      commonjsOptions: {
        ignoreTryCatch: false
      }
    }
  };
});
