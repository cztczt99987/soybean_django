import type { FlatResponseData } from '@sa/axios';
import { request } from '../request';

type Query = Record<string, any>;

function qs(params?: Query) {
  if (!params) return '';
  const search = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === null || v === undefined || v === '') return;
    if (Array.isArray(v)) {
      v.forEach(i => search.append(k, String(i)));
    } else {
      search.set(k, String(v));
    }
  });
  const s = search.toString();
  return s ? `?${s}` : '';
}

/** ========== 通用 CRUD 工具 ========== */

function list<T>(url: string, params?: Query) {
  return request<T>({ url: url + qs(params), method: 'get' });
}
function tree<T>(url: string, params?: Query) {
  return request<T>({ url: url + qs(params), method: 'get' });
}
function detail<T>(url: string, id: number | string) {
  return request<T>({ url: `${url}/${id}`, method: 'get' });
}
function add<T>(url: string, data: any) {
  return request<T>({ url, method: 'post', data });
}
function update<T>(url: string, id: number | string, data: any) {
  return request<T>({ url: `${url}/${id}`, method: 'put', data });
}
function remove(url: string, id: number | string) {
  return request<boolean>({ url: `${url}/${id}`, method: 'delete' });
}
function batchDelete(url: string, ids: (number | string)[]) {
  return request<boolean>({ url: `${url}/batch-delete`, method: 'post', data: { ids } });
}

/** ========== 用户 ========== */

export const userApi = {
  list: (params?: Api.System.UserSearchParams) =>
    list<Api.System.ListResp<Api.System.User>>('/system/user/', params),
  add: (data: Partial<Api.System.User>) => add<Api.System.User>('/system/user/', data),
  update: (id: number, data: Partial<Api.System.User>) =>
    update<Api.System.User>('/system/user/', id, data),
  remove: (id: number) => remove('/system/user/', id),
  batchDelete: (ids: number[]) => batchDelete('/system/user/', ids),
  resetPwd: (id: number, password?: string) =>
    request<boolean>({ url: `/system/user/${id}/reset-pwd`, method: 'post', data: { password } }),
  changeStatus: (id: number, status: '1' | '0') =>
    request<boolean>({ url: `/system/user/${id}/change-status`, method: 'post', data: { status } })
};

/** ========== 角色 ========== */

export const roleApi = {
  list: (params?: Api.System.RoleSearchParams) =>
    list<Api.System.ListResp<Api.System.Role>>('/system/role/', params),
  options: () => request<{ id: number; name: string; code: string }[]>({ url: '/system/role/options/' }),
  add: (data: Partial<Api.System.Role>) => add<Api.System.Role>('/system/role/', data),
  update: (id: number, data: Partial<Api.System.Role>) =>
    update<Api.System.Role>('/system/role/', id, data),
  remove: (id: number) => remove('/system/role/', id),
  batchDelete: (ids: number[]) => batchDelete('/system/role/', ids),
  assignMenus: (id: number, menuIds: number[]) =>
    request<boolean>({ url: `/system/role/${id}/assign-menus`, method: 'post', data: { menuIds } })
};

/** ========== 菜单 ========== */

export const menuApi = {
  list: (params?: Api.System.SearchParams) =>
    list<Api.System.ListResp<Api.System.Menu>>('/system/menu/', params),
  tree: (params?: Api.System.SearchParams) => tree<Api.System.Menu[]>('/system/menu/tree/', params),
  options: () => request<any[]>({ url: '/system/menu/options/' }),
  add: (data: Partial<Api.System.Menu>) => add<Api.System.Menu>('/system/menu/', data),
  update: (id: number, data: Partial<Api.System.Menu>) =>
    update<Api.System.Menu>('/system/menu/', id, data),
  remove: (id: number) => remove('/system/menu/', id),
  batchDelete: (ids: number[]) => batchDelete('/system/menu/', ids)
};

/** ========== 部门 ========== */

export const deptApi = {
  list: (params?: Api.System.SearchParams) =>
    list<Api.System.ListResp<Api.System.Department>>('/system/dept/', params),
  tree: (params?: Api.System.SearchParams) =>
    tree<Api.System.Department[]>('/system/dept/tree/', params),
  options: () => request<any[]>({ url: '/system/dept/options/' }),
  add: (data: Partial<Api.System.Department>) =>
    add<Api.System.Department>('/system/dept/', data),
  update: (id: number, data: Partial<Api.System.Department>) =>
    update<Api.System.Department>('/system/dept/', id, data),
  remove: (id: number) => remove('/system/dept/', id),
  batchDelete: (ids: number[]) => batchDelete('/system/dept/', ids)
};

/** ========== 岗位 ========== */

export const postApi = {
  list: (params?: Api.System.PostSearchParams) =>
    list<Api.System.ListResp<Api.System.Post>>('/system/post/', params),
  options: () => request<{ id: number; name: string; code: string }[]>({ url: '/system/post/options/' }),
  add: (data: Partial<Api.System.Post>) => add<Api.System.Post>('/system/post/', data),
  update: (id: number, data: Partial<Api.System.Post>) =>
    update<Api.System.Post>('/system/post/', id, data),
  remove: (id: number) => remove('/system/post/', id),
  batchDelete: (ids: number[]) => batchDelete('/system/post/', ids)
};

/** ========== 字典类型 ========== */

export const dictTypeApi = {
  list: (params?: Api.System.DictTypeSearchParams) =>
    list<Api.System.ListResp<Api.System.DictType>>('/system/dict/type/', params),
  options: () => request<{ id: number; name: string; code: string }[]>({ url: '/system/dict/type/options/' }),
  items: (id: number) => request<Api.System.DictData[]>({ url: `/system/dict/type/${id}/items/` }),
  add: (data: Partial<Api.System.DictType>) => add<Api.System.DictType>('/system/dict/type/', data),
  update: (id: number, data: Partial<Api.System.DictType>) =>
    update<Api.System.DictType>('/system/dict/type/', id, data),
  remove: (id: number) => remove('/system/dict/type/', id),
  batchDelete: (ids: number[]) => batchDelete('/system/dict/type/', ids)
};

/** ========== 字典明细 ========== */

export const dictDataApi = {
  list: (params?: Api.System.DictDataSearchParams) =>
    list<Api.System.ListResp<Api.System.DictData>>('/system/dict/data/', params),
  byCode: (code: string) =>
    request<Api.System.DictData[]>({ url: `/system/dict/data/by-code/?code=${encodeURIComponent(code)}` }),
  add: (data: Partial<Api.System.DictData>) => add<Api.System.DictData>('/system/dict/data/', data),
  update: (id: number, data: Partial<Api.System.DictData>) =>
    update<Api.System.DictData>('/system/dict/data/', id, data),
  remove: (id: number) => remove('/system/dict/data/', id),
  batchDelete: (ids: number[]) => batchDelete('/system/dict/data/', ids)
};

/** ========== 参数设置 ========== */

export const configApi = {
  list: (params?: Api.System.ConfigSearchParams) =>
    list<Api.System.ListResp<Api.System.Config>>('/system/config/', params),
  byKey: (code: string) =>
    request<Api.System.Config | null>({ url: `/system/config/by-key/?code=${encodeURIComponent(code)}` }),
  add: (data: Partial<Api.System.Config>) => add<Api.System.Config>('/system/config/', data),
  update: (id: number, data: Partial<Api.System.Config>) =>
    update<Api.System.Config>('/system/config/', id, data),
  remove: (id: number) => remove('/system/config/', id),
  batchDelete: (ids: number[]) => batchDelete('/system/config/', ids)
};

/** ========== 操作日志 ========== */

export const logApi = {
  list: (params?: Api.System.SearchParams) =>
    list<Api.System.ListResp<Api.System.OperationLog>>('/system/log/', params),
  remove: (id: number) => remove('/system/log/', id),
  batchDelete: (ids: number[]) => batchDelete('/system/log/', ids),
  clean: (days?: number) =>
    request<{ deleted: number }>({ url: '/system/log/clean/', method: 'post', data: { days } })
};
