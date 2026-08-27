/**
 * Namespace Api.System
 *
 * 系统管理模块的前后端接口类型（用户/角色/菜单/部门/岗位/字典类型/字典明细/参数/操作日志）
 */
declare namespace Api {
  namespace System {
    /** 前后端统一的分页查询返回体，current/size/total/records */
    type ListResp<T> = Api.Common.PaginatingQueryRecord<T>;

    interface BaseRow {
      id: number;
      sort_order?: number;
      remark?: string;
      created_at: string;
      updated_at: string;
    }

    interface Department extends BaseRow {
      departmentId: number;
      parentId: number | null;
      name: string;
      code: string;
      leader: string;
      phone: string;
      email: string;
      status: '1' | '0';
      children?: Department[];
    }

    interface Post extends BaseRow {
      postId: number;
      name: string;
      code: string;
      status: '1' | '0';
    }

    interface Role extends BaseRow {
      roleId: number;
      name: string;
      code: string;
      status: '1' | '0';
      data_scope: '1' | '2' | '3' | '4' | '5';
      menus: number[];
      departments: number[];
      /** 前端写接口提交用 */
      menuIds?: number[];
      departmentIds?: number[];
    }

    interface Menu extends BaseRow {
      menuId: number;
      parentId: number | null;
      name: string;
      title: string;
      path: string;
      component: string;
      permission: string;
      icon: string;
      menu_type: '1' | '2' | '3';
      order: number;
      i18n_key: string;
      keep_alive: boolean;
      hide_in_menu: boolean;
      external_link: string;
      status: '1' | '0';
      children?: Menu[];
    }

    interface User extends BaseRow {
      userId: number;
      username: string;
      nickname: string;
      avatar: string;
      email: string;
      phone: string;
      gender: '0' | '1' | '2';
      department_id?: number | null;
      dept?: { id: number; name: string; code: string } | null;
      roles: Role[];
      posts: Post[];
      status: '1' | '0';
      /** 提交时使用 */
      roleIds?: number[];
      postIds?: number[];
      password?: string;
      login_ip?: string;
      login_at?: string;
    }

    interface DictType extends BaseRow {
      dictId: number;
      name: string;
      code: string;
      status: '1' | '0';
      items?: DictData[];
    }

    interface DictData extends BaseRow {
      id: number;
      dictCode: string;
      label: string;
      value: string;
      css_class: string;
      list_class: string;
      is_default: boolean;
      status: '1' | '0';
      /** 创建时使用 */
      dictCodeInput?: string;
    }

    interface Config extends BaseRow {
      configId: number;
      name: string;
      code: string;
      value: string;
      value_type: 'S' | 'N' | 'B' | 'J';
      is_system: boolean;
      status: '1' | '0';
    }

    interface OperationLog extends BaseRow {
      logId: number;
      user?: { id: number; username: string; nickname: string } | null;
      username: string;
      module: string;
      description: string;
      operation_type: '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9';
      method: string;
      request_url: string;
      request_params: string;
      ip: string;
      location: string;
      response_result: string;
      status: '1' | '0';
      cost_time: number;
      error_msg: string;
      operated_at: string;
    }

    /** 搜索参数通用 */
    interface SearchParams {
      current?: number;
      size?: number;
      keyword?: string;
      status?: '1' | '0' | '';
      beginTime?: string;
      endTime?: string;
      [key: string]: any;
    }
  }
}
