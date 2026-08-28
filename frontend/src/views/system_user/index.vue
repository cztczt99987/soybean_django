<script setup lang="ts">
import { computed, h, reactive, ref, watch } from 'vue';
import { useMessage, useDialog, NSwitch, type FormInst, type FormRules } from 'naive-ui';
import type { FlatResponseData } from '@sa/axios';
import { $t } from '@/locales';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { userApi, deptApi, roleApi, postApi } from '@/service/api';

const message = useMessage();
const dialog = useDialog();

const formRef = ref<FormInst | null>(null);
const queryForm = reactive<{
  keyword: string;
  status: '' | '1' | '0';
  deptId: number | null;
  beginTime: string | null;
  endTime: string | null;
  dateRange: [string, string] | null;
}>({
  keyword: '',
  status: '',
  deptId: null,
  beginTime: null,
  endTime: null,
  dateRange: null
});

const drawerFormRef = ref<FormInst | null>(null);
const drawerForm = reactive<{
  username: string;
  nickname: string;
  password: string;
  email: string;
  phone: string;
  gender: '0' | '1' | '2';
  department_id: number | null;
  roleIds: number[];
  postIds: number[];
  status: '1' | '0';
  remark: string;
}>({
  username: '',
  nickname: '',
  password: '',
  email: '',
  phone: '',
  gender: '0',
  department_id: null,
  roleIds: [],
  postIds: [],
  status: '1',
  remark: ''
});

const deptOptions = ref<Api.System.Department[]>([]);
const roleOptions = ref<{ id: number; name: string; code: string }[]>([]);
const postOptions = ref<{ id: number; name: string; code: string }[]>([]);

async function loadOptions() {
  const [deptRes, roleRes, postRes] = await Promise.all([
    deptApi.tree(),
    roleApi.options(),
    postApi.options()
  ]);
  if (!deptRes.error) deptOptions.value = deptRes.data || [];
  if (!roleRes.error) roleOptions.value = roleRes.data || [];
  if (!postRes.error) postOptions.value = postRes.data || [];
}
loadOptions();

type Row = Api.System.User;
type Resp = FlatResponseData<App.Service.Response, Api.System.ListResp<Row>>;
type TableInst = ReturnType<typeof useNaivePaginatedTable<Resp, Row>>;

// 先声明为 undefined 再赋值：api 闭包首次同步调用时 tbl 尚未就绪，需可选链兜底（不能改 const，否则 TDZ）
let tbl: TableInst | undefined;
// eslint-disable-next-line prefer-const
tbl = useNaivePaginatedTable<Resp, Row>({
  api: () => {
    const params: Api.System.SearchParams = {
      current: tbl?.pagination?.page ?? 1,
      size: tbl?.pagination?.pageSize ?? 10,
      keyword: queryForm.keyword || undefined,
      status: queryForm.status || undefined,
      deptId: queryForm.deptId ?? undefined,
      beginTime: queryForm.dateRange?.[0],
      endTime: queryForm.dateRange?.[1]
    };
    return userApi.list(params);
  },
  columns: () => [
    { type: 'selection', width: 60 },
    {
      title: $t('common.index'),
      key: '__index__',
      width: 64,
      render: (_row, rowIndex) => ((tbl?.pagination?.page ?? 1) - 1) * (tbl?.pagination?.pageSize ?? 10) + rowIndex + 1
    },
    { title: 'ID', key: 'id', width: 80 },
    { title: $t('page.system.user.form.username'), key: 'username', width: 140 },
    { title: $t('page.system.user.form.nickname'), key: 'nickname', width: 140 },
    {
      title: $t('page.system.user.form.dept'),
      key: 'dept.name',
      width: 140,
      render: row => (row.dept ? row.dept.name : '-')
    },
    { title: $t('page.system.user.form.phone'), key: 'phone', width: 140 },
    { title: $t('page.system.user.form.email'), key: 'email', width: 180 },
    {
      title: $t('page.system.user.form.gender'),
      key: 'gender',
      width: 80,
      render: row =>
        ({
          '0': $t('page.system.common.gender.unknown'),
          '1': $t('page.system.common.gender.male'),
          '2': $t('page.system.common.gender.female')
        })[row.gender] || '-'
    },
    {
      title: $t('page.system.user.form.status'),
      key: 'status',
      width: 120,
      render: row =>
        h(
          NSwitch,
          {
            value: row.status === '1',
            onUpdateValue: (val: boolean) => {
              changeStatus(row.id, val);
            },
            checkedValue: true,
            uncheckedValue: false
          },
          {
            checked: () => $t('page.system.common.enabled'),
            unchecked: () => $t('page.system.common.disabled')
          }
        )
    },
    { title: $t('page.system.common.createdAt'), key: 'created_at', width: 180 },
    {
      title: $t('common.operate'),
      key: 'actions',
      width: 300,
      fixed: 'right',
      render: row =>
        h('div', { style: { display: 'flex', gap: '8px', alignItems: 'center' } }, [
          createButtonResetPwd(row),
          createButtonEdit(row),
          createButtonDelete(row)
        ])
    }
  ],
  transform: defaultTransform
});

const { data, loading, columns, columnChecks, getData, getDataByPage, mobilePagination } = tbl;
const {
  drawerVisible,
  closeDrawer,
  operateType,
  handleAdd,
  editingData,
  handleEdit,
  checkedRowKeys,
  onBatchDeleted,
  onDeleted
} = useTableOperate(data, 'id', getData);

const drawerRules = computed<FormRules>(() => ({
  username: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  nickname: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  password: [
    {
      required: operateType.value === 'add',
      message: $t('form.required'),
      trigger: 'blur'
    }
  ],
  email: [
    {
      required: true,
      message: $t('form.email.required'),
      trigger: 'blur'
    },
    {
      type: 'email',
      message: $t('form.email.invalid'),
      trigger: 'blur'
    }
  ],
  phone: [{ required: true, message: $t('form.phone.required'), trigger: 'blur' }],
  status: [{ required: true, message: $t('form.required'), trigger: 'change' }]
}));

watch(
  editingData,
  v => {
    if (v) {
      Object.assign(drawerForm, {
        username: v.username || '',
        nickname: v.nickname || '',
        password: '',
        email: v.email || '',
        phone: v.phone || '',
        gender: v.gender || '0',
        department_id: v.department_id || null,
        roleIds: v.roles ? v.roles.map(r => r.id) : [],
        postIds: v.posts ? v.posts.map(p => p.id) : [],
        status: v.status || '1',
        remark: v.remark || ''
      });
    } else {
      Object.assign(drawerForm, defaultForm());
    }
  },
  { immediate: true }
);

function defaultForm() {
  return {
    username: '',
    nickname: '',
    password: '',
    email: '',
    phone: '',
    gender: '0' as const,
    department_id: null,
    roleIds: [],
    postIds: [],
    status: '1' as const,
    remark: ''
  };
}

async function onSubmit() {
  const valid = await drawerFormRef.value?.validate().catch(() => false);
  if (!valid) {
    message.warning($t('common.pleaseCheckValue'));
    return;
  }
  const payload: Partial<typeof drawerForm> = { ...drawerForm };
  if (operateType.value === 'edit' && !payload.password) {
    delete payload.password;
  }
  const { error } =
    operateType.value === 'add'
      ? await userApi.add(payload)
      : await userApi.update(editingData.value!.id, payload);
  if (error) return;
  message.success(operateType.value === 'add' ? $t('common.addSuccess') : $t('common.modifySuccess'));
  closeDrawer();
  await getData();
}

async function changeStatus(id: number, val: boolean) {
  const { error } = await userApi.changeStatus(id, val ? '1' : '0');
  if (!error) {
    message.success($t('page.system.common.changeStatusSuccess'));
    await getData();
  }
}

function createButtonEdit(row: Row) {
  return h(
    'NButton',
    {
      size: 'small',
      type: 'primary',
      ghost: true,
      onClick: () => handleEdit(row.id)
    },
    { default: () => $t('common.edit') }
  );
}

function createButtonDelete(row: Row) {
  return h(
    'NPopconfirm',
    {
      onPositiveClick: async () => {
        const { error } = await userApi.remove(row.id);
        if (!error) onDeleted();
      }
    },
    {
      trigger: () =>
        h(
          'NButton',
          {
            size: 'small',
            type: 'error',
            ghost: true
          },
          { default: () => $t('common.delete') }
        ),
      default: () => $t('common.confirmDelete')
    }
  );
}

function createButtonResetPwd(row: Row) {
  return h(
    'NPopconfirm',
    {
      onPositiveClick: async () => {
        const { error } = await userApi.resetPwd(row.id);
        if (!error) message.success($t('page.system.common.resetPwdSuccess'));
      }
    },
    {
      trigger: () =>
        h(
          'NButton',
          {
            size: 'small',
            type: 'warning',
            ghost: true
          },
          { default: () => $t('page.system.user.action.resetPwd') }
        ),
      default: () => $t('page.system.common.resetPwdConfirm')
    }
  );
}

async function onBatchDelete() {
  if (!checkedRowKeys.value.length) return;
  dialog.warning({
    title: $t('common.warning'),
    content: $t('common.confirmDelete'),
    positiveText: $t('common.confirm'),
    negativeText: $t('common.cancel'),
    onPositiveClick: async () => {
      const ids = checkedRowKeys.value.map(Number);
      const { error } = await userApi.batchDelete(ids);
      if (!error) onBatchDeleted();
    }
  });
}

function onSearch() {
  getDataByPage();
}
function onReset() {
  Object.assign(queryForm, {
    keyword: '',
    status: '',
    deptId: null,
    beginTime: null,
    endTime: null,
    dateRange: null
  });
  onSearch();
}
</script>

<template>
  <div class="min-h-full">
    <NSpace vertical :size="12">
      <NCard>
        <NForm ref="formRef" inline label-placement="left" label-width="auto" :model="queryForm">
          <NFormItem :label="$t('common.keywordSearch')">
            <NInput
              v-model:value="queryForm.keyword"
              clearable
              :placeholder="$t('common.keywordSearch')"
            />
          </NFormItem>
          <NFormItem :label="$t('page.system.user.form.status')">
            <NSelect
              v-model:value="queryForm.status"
              :options="[
                { label: $t('page.system.common.enabled'), value: '1' },
                { label: $t('page.system.common.disabled'), value: '0' }
              ]"
              clearable
            />
          </NFormItem>
          <NFormItem :label="$t('page.system.user.form.dept')">
            <NTreeSelect
              v-model:value="queryForm.deptId"
              :options="deptOptions"
              key-field="id"
              label-field="name"
              children-field="children"
              clearable
            />
          </NFormItem>
          <NFormItem :label="$t('page.system.common.dateRange')">
            <NDatePicker
              v-model:formatted-value="queryForm.dateRange"
              type="daterange"
              value-format="yyyy-MM-dd"
              clearable
            />
          </NFormItem>
          <NFormItem>
            <NSpace>
              <NButton type="primary" @click="onSearch">
                <template #icon><icon-mdi-magnify class="text-icon" /></template>{{ $t('common.search') }}
              </NButton>
              <NButton @click="onReset">
                <template #icon><icon-mdi-refresh class="text-icon" /></template>{{ $t('common.reset') }}
              </NButton>
            </NSpace>
          </NFormItem>
        </NForm>
      </NCard>

      <NCard :bordered="false" class="!mt-0">
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :loading="loading"
          :disabled-delete="!checkedRowKeys.length"
          @add="handleAdd"
          @delete="onBatchDelete"
          @refresh="getData"
        />

        <NDataTable
          v-model:checked-row-keys="checkedRowKeys"
          :columns="columns"
          :data="data"
          :loading="loading"
          :pagination="mobilePagination"
          :scroll-x="1700"
          :bordered="false"
          striped
        />
      </NCard>
    </NSpace>

    <NDrawer v-model:show="drawerVisible" :width="640" placement="right" :mask-closable="false">
      <NDrawerContent
        :title="operateType === 'add' ? $t('common.add') : $t('common.edit')"
        :closable="true"
      >
        <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
          <NButton size="small" @click="closeDrawer">{{ $t('common.close') }}</NButton>
        </div>
        <NForm ref="drawerFormRef" label-placement="top" :model="drawerForm" :rules="drawerRules">
          <NFormItem :label="$t('page.system.user.form.username')" path="username">
            <NInput v-model:value="drawerForm.username" />
          </NFormItem>
          <NFormItem :label="$t('page.system.user.form.nickname')" path="nickname">
            <NInput v-model:value="drawerForm.nickname" />
          </NFormItem>
          <NFormItem
            v-if="operateType === 'add'"
            :label="$t('page.system.user.form.password')"
            path="password"
          >
            <NInput v-model:value="drawerForm.password" type="password" show-password-on="click" />
          </NFormItem>
          <NFormItem :label="$t('page.system.user.form.email')" path="email">
            <NInput v-model:value="drawerForm.email" />
          </NFormItem>
          <NFormItem :label="$t('page.system.user.form.phone')" path="phone">
            <NInput v-model:value="drawerForm.phone" />
          </NFormItem>
          <NFormItem :label="$t('page.system.user.form.gender')" path="gender">
            <NRadioGroup v-model:value="drawerForm.gender">
              <NRadio value="0">{{ $t('page.system.common.gender.unknown') }}</NRadio>
              <NRadio value="1">{{ $t('page.system.common.gender.male') }}</NRadio>
              <NRadio value="2">{{ $t('page.system.common.gender.female') }}</NRadio>
            </NRadioGroup>
          </NFormItem>
          <NFormItem :label="$t('page.system.user.form.dept')" path="department_id">
            <NTreeSelect
              v-model:value="drawerForm.department_id"
              :options="deptOptions"
              key-field="id"
              label-field="name"
              children-field="children"
              clearable
            />
          </NFormItem>
          <NFormItem :label="$t('page.system.user.form.roles')" path="roleIds">
            <NSelect
              v-model:value="drawerForm.roleIds"
              multiple
              :options="roleOptions.map(r => ({ label: r.name, value: r.id }))"
            />
          </NFormItem>
          <NFormItem :label="$t('page.system.user.form.posts')" path="postIds">
            <NSelect
              v-model:value="drawerForm.postIds"
              multiple
              :options="postOptions.map(p => ({ label: p.name, value: p.id }))"
            />
          </NFormItem>
          <NFormItem :label="$t('page.system.user.form.status')" path="status">
            <NRadioGroup v-model:value="drawerForm.status">
              <NRadio value="1">{{ $t('page.system.common.enabled') }}</NRadio>
              <NRadio value="0">{{ $t('page.system.common.disabled') }}</NRadio>
            </NRadioGroup>
          </NFormItem>
          <NFormItem :label="$t('page.system.user.form.remark')" path="remark">
            <NInput v-model:value="drawerForm.remark" type="textarea" :rows="3" />
          </NFormItem>
        </NForm>
        <template #footer>
          <NSpace justify="end">
            <NButton @click="closeDrawer">{{ $t('common.cancel') }}</NButton>
            <NButton type="primary" :loading="loading" @click="onSubmit">{{ $t('common.confirm') }}</NButton>
          </NSpace>
        </template>
      </NDrawerContent>
    </NDrawer>
  </div>
</template>
