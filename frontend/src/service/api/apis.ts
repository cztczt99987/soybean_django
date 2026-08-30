/**
 * Swagger 文档地址
 *
 * 开发环境走 vite 代理（/proxy-default → 后端 /api），保证 iframe 同源嵌入；
 * 生产环境直接指向 VITE_SERVICE_BASE_URL（需反向代理保证同源）。
 */
export function getSwaggerDocsUrl() {
  const useProxy = import.meta.env.DEV && import.meta.env.VITE_HTTP_PROXY === 'Y';
  return useProxy ? '/proxy-default/docs/' : `${import.meta.env.VITE_SERVICE_BASE_URL}/docs/`;
}
