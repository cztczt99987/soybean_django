import { request } from '../request';

/** ========== 服务器信息 ========== */

export const serverApi = {
  info: () => request<Api.Monitor.ServerInfo>({ url: '/monitor/server' })
};

/** ========== Redis 缓存管理 ========== */

export const cacheApi = {
  list: (params?: Api.Monitor.CacheSearchParams) =>
    request<Api.Monitor.CacheListResp>({
      url: '/monitor/cache',
      params: { keyword: params?.keyword || undefined }
    }),
  remove: (key: string) =>
    request<{ deleted: number }>({ url: '/monitor/cache/delete', method: 'post', data: { key } }),
  batchRemove: (keys: string[]) =>
    request<{ deleted: number }>({ url: '/monitor/cache/delete', method: 'post', data: { keys } }),
  cleanAll: () =>
    request<{ deleted: number }>({ url: '/monitor/cache/delete', method: 'post', data: { all: true } })
};

/** ========== 文件管理 ========== */

export const fileApi = {
  list: (path = '') =>
    request<Api.Monitor.FileListResp>({ url: '/monitor/files', params: { path } }),
  download: (path: string) =>
    request<Blob, 'blob'>({ url: '/monitor/file/download', params: { path }, responseType: 'blob' })
};

/** ========== 存储配置 ========== */

export const storageApi = {
  get: (type: Api.Monitor.StorageType) =>
    request<Api.Monitor.StorageConfigResp>({ url: '/monitor/storage', params: { type } }),
  save: (type: Api.Monitor.StorageType, config: Record<string, unknown>) =>
    request<boolean>({ url: '/monitor/storage', method: 'post', data: { type, config } }),
  validate: (type: Api.Monitor.StorageType, config: Record<string, unknown>) =>
    request<{ valid: boolean }>({ url: '/monitor/storage', method: 'post', data: { type, config, validate: true } }),
  switchActive: (type: Api.Monitor.StorageType) =>
    request<boolean>({ url: '/monitor/storage', method: 'post', data: { active: type } })
};
