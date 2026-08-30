import { request } from '../request';

type Query = Record<string, any>;

function qs(params?: Query) {
  if (!params) return '';
  const search = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === null || v === undefined || v === '') return;
    search.set(k, String(v));
  });
  const s = search.toString();
  return s ? `?${s}` : '';
}

/** 拼接路径: 保留尾斜杠 (DRF 路由要求) */
function joinUrl(base: string, sub?: string | number) {
  return sub === undefined ? base : `${base.replace(/\/+$/, '')}/${sub}/`;
}

function list<T>(url: string, params?: Query) {
  return request<T>({ url: url + qs(params), method: 'get' });
}
function add<T>(url: string, data: any) {
  return request<T>({ url, method: 'post', data });
}
function update<T>(url: string, id: number | string, data: any) {
  return request<T>({ url: joinUrl(url, id), method: 'put', data });
}
function remove(url: string, id: number | string) {
  return request<boolean>({ url: joinUrl(url, id), method: 'delete' });
}

/** ========== 定时任务 ========== */

export const taskJobApi = {
  list: (params?: Api.Task.TaskJobSearchParams) =>
    list<Api.Task.ListResp<Api.Task.TaskJob>>('/task/job/', params),
  add: (data: Partial<Api.Task.TaskJob>) => add<Api.Task.TaskJob>('/task/job/', data),
  update: (id: number, data: Partial<Api.Task.TaskJob>) =>
    update<Api.Task.TaskJob>('/task/job/', id, data),
  remove: (id: number) => remove('/task/job/', id),
  pause: (id: number) => request<boolean>({ url: `/task/job/${id}/pause/`, method: 'post' }),
  resume: (id: number) => request<boolean>({ url: `/task/job/${id}/resume/`, method: 'post' }),
  /** 立即执行一次 */
  runOnce: (id: number) => request<boolean>({ url: `/task/job/${id}/run-once/`, method: 'post' }),
  /** 任务执行历史 */
  logs: (id: number, params?: Api.Task.LogSearchParams) =>
    list<Api.Task.ListResp<Api.Task.ExecutionLog>>(`/task/job/${id}/logs/`, params),
  /** 内置处理器清单 */
  handlers: () => request<{ key: string; label: string }[]>({ url: '/task/job/handlers/' })
};

/** ========== 执行日志 ========== */

export const taskLogApi = {
  list: (params?: Api.Task.LogSearchParams) =>
    list<Api.Task.ListResp<Api.Task.ExecutionLog>>('/task/log/', params),
  clear: () => request<{ deleted: number }>({ url: '/task/log/clear/', method: 'post' })
};

/** ========== 执行节点 ========== */

export const taskNodeApi = {
  list: (params?: Api.Task.NodeSearchParams) =>
    list<Api.Task.ListResp<Api.Task.SchedulerNode>>('/task/node/', params),
  add: (data: Partial<Api.Task.SchedulerNode>) => add<Api.Task.SchedulerNode>('/task/node/', data),
  update: (id: number, data: Partial<Api.Task.SchedulerNode>) =>
    update<Api.Task.SchedulerNode>('/task/node/', id, data),
  remove: (id: number) => remove('/task/node/', id),
  /** 启用/禁用切换 */
  toggle: (id: number) =>
    request<Api.Task.SchedulerNode>({ url: `/task/node/${id}/toggle/`, method: 'post' })
};

/** ========== 调度器监控 ========== */

export const schedulerApi = {
  status: () => request<Api.Task.SchedulerStatus>({ url: '/task/scheduler/status' }),
  /** action: start | pause | resume | shutdown | clear | reload */
  control: (action: string) =>
    request<Api.Task.SchedulerStatus>({ url: '/task/scheduler/control', method: 'post', data: { action } }),
  console: (keyword?: string) =>
    request<Api.Task.ConsoleLog[]>({ url: `/task/scheduler/console${qs({ keyword })}` })
};
