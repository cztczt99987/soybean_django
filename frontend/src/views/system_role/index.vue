<script setup lang="ts">
import { computed, h, reactive, ref, watch } from 'vue';
import { useMessage, useDialog, type FormInst, type FormRules } from 'naive-ui';
import { $t } from '@/locales';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { roleApi, menuApi, deptApi } from '@/service/api';

const message = useMessage();
const dialog = useDialog();

const formRef = ref<FormInst | null>(null);
const queryForm = reactive<{
  keyword: string;
  status: '' | '1' | '0';
}>({
  keyword: '',
  status: ''
});

const drawerFormRef = ref<FormInst | null>(null);
const drawerForm = reactive<{
  name: string;
  code: string;
  data_scope: '1' | '2' | '3' | '4' | '5';
  status: '1' | '0';
  menuIds: number[];
  departmentIds: number[];
  remark: string;
}>({
  name: '',
  code: '',
  data_scope: '1',
  status: '1',
  menuIds: [],
  departmentIds: [],
  remark: ''
});

const menuTree = ref<any[]>([]);
const deptTree = ref<any[]>([]);

async function loadOptions() {
  const [menuRes, deptRes] = await Promise.all([menuApi.tree(), deptApi.tree()]);
  if (!menuRes.error) menuTree.value = menuRes.data || [];
  if (!deptRes.error) deptTree.value = deptRes.data || [];
}
loadOptions();

const drawerRules = computed<FormRules>(() => ({
  name: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  code: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  data_scope: [{ required: true, message: $t('form.required'), trigger: 'change' }],
  status: [{ required: true, message: $t('form.required'), trigger: 'change' }]
}));

const dataScopeOptions = [
  { label: '全部数据权限', value: '1' },
  { label: '自定数据权限', value: '2' },
  { label: '本部门数据权限', value: '3' },
  { label: '本部门及以下数据权限', value: '4' },
  { label: '仅本人数据权限', value: '5' }
];

const tbl: any = useNaivePaginatedTable({
  api: () => {
    const params: any = { current: tbl.pagination.page, size: tbl.pagination.pageSize };
    Object.entries(queryForm).forEach(([k, v]) => {
      if (v !== '' && v !== null && v !== undefined) params[k] = v;
    });
    return roleApi.list(params);
  },
  columns: () => [
    { type: 'selection', width: 60 },
    {
      title: '#',
      key: '__index__',
      width: 64,
      render: (...args: any[]): any => {
        const index = args.length >= 3 ? args[2] : args[1];
        return (tbl.pagination.page - 1) * tbl.pagination.pageSize + index + 1;
      }
    },
    { title: 'ID', key: 'id', width: 80 },
    { title: $t('page.system.role.form.name'), key: 'name', width: 160 },
    { title: $t('page.system.role.form.code'), key: 'code', width: 160 },
    {
      title: $t('page.system.role.form.dataScope'),
      key: 'data_scope',
      width: 180,
      render: (row: any) => dataScopeOptions.find(o => o.value === row.data_scope)?.label || '-'
    },
    {
      title: $t('page.system.role.form.status'),
      key: 'status',
      width: 100,
      render: (row: any) =>
        h(
          'span',
          {
            style: {
              color: row.status === '1' ? '#18a058' : '#d03050'
            }
          },
          row.status === '1' ? '正常' : '停用'
        )
    },
    { title: $t('page.system.role.form.remark'), key: 'remark', width: 200 },
    { title: '创建时间', key: 'created_at', width: 180 },
    {
      title: $t('common.operate'),
      key: 'actions',
      width: 260,
      fixed: 'right',
      render: (row: any): any =>
        h('div', { style: { display: 'flex', gap: '8px' } }, [
          createButtonAssignMenus(row),
          createButtonEdit(row),
          createButtonDelete(row)
        ])
    }
  ],
  transform: defaultTransform as any
} as any);

const loading = tbl.loading;
const data = tbl.data;
const columns = tbl.columns;
const columnChecks = tbl.columnChecks;
const getData = tbl.getData;
const pagination = tbl.pagination;
const mobilePagination = tbl.mobilePagination;

const ops: any = (useTableOperate as any)(data, 'id', getData);
const drawerVisible = ops.drawerVisible;
const openDrawer = ops.openDrawer;
const closeDrawer = ops.closeDrawer;
const operateType = ops.operateType;
const handleAdd = ops.handleAdd;
const editingData = ops.editingData;
const handleEdit = ops.handleEdit;
const checkedRowKeys = ops.checkedRowKeys;
const onBatchDeleted = ops.onBatchDeleted;
const onDeleted = ops.onDeleted;

watch(
  editingData,
  (v: any) => {
    if (v) {
      Object.assign(drawerForm, {
        name: v.name || '',
        code: v.code || '',
        data_scope: v.data_scope || '1',
        status: v.status || '1',
        menuIds: v.menuIds || v.menus || [],
        departmentIds: v.departmentIds || v.departments || [],
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
    name: '',
    code: '',
    data_scope: '1' as const,
    status: '1' as const,
    menuIds: [],
    departmentIds: [],
    remark: ''
  };
}

async function onSubmit() {
  const valid = await drawerFormRef.value?.validate().catch(() => false);
  if (!valid) {
    message.warning($t('common.pleaseCheckValue'));
    return;
  }
  const payload: any = { ...drawerForm };
  const { error } =
    operateType.value === 'add'
      ? await roleApi.add(payload)
      : await roleApi.update(editingData.value!.id, payload);
  if (error) return;
  message.success(operateType.value === 'add' ? $t('common.addSuccess') : $t('common.modifySuccess'));
  closeDrawer();
  await getData();
}

function createButtonEdit(row: any): any {
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

function createButtonDelete(row: any): any {
  return h(
    'NPopconfirm',
    {
      onPositiveClick: async () => {
        const { error } = await roleApi.remove(row.id);
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

function createButtonAssignMenus(row: any): any {
  return h(
    'NButton',
    {
      size: 'small',
      type: 'info',
      ghost: true,
      onClick: () => openAssignMenus(row)
    },
    { default: () => $t('page.system.role.action.assignMenus') }
  );
}

const assignMenusVisible = ref(false);
const assignMenusRoleId = ref<number | null>(null);
const assignMenusSelected = ref<number[]>([]);

function openAssignMenus(row: any) {
  assignMenusRoleId.value = row.id;
  assignMenusSelected.value = row.menus || [];
  assignMenusVisible.value = true;
}

async function onAssignMenusSubmit() {
  if (!assignMenusRoleId.value) return;
  const { error } = await roleApi.assignMenus(assignMenusRoleId.value, assignMenusSelected.value);
  if (!error) {
    message.success('分配菜单成功');
    assignMenusVisible.value = false;
    await getData();
  }
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
      const { error } = await roleApi.batchDelete(ids);
      if (!error) onBatchDeleted();
    }
  });
}

function onSearch() {
  pagination.page = 1;
  getData();
}
function onReset() {
  Object.assign(queryForm, {
    keyword: '',
    status: ''
  });
  onSearch();
}
</script>

<template>
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
        <NFormItem :label="$t('page.system.role.form.status')">
          <NSelect
            v-model:value="queryForm.status"
            :options="[
              { label: '正常', value: '1' },
              { label: '停用', value: '0' }
            ]"
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
        :columns="columns"
        :data="data"
        :loading="loading"
        :pagination="mobilePagination"
        v-model:checked-row-keys="checkedRowKeys"
        :scroll-x="1500"
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
        <NFormItem :label="$t('page.system.role.form.name')" path="name">
          <NInput v-model:value="drawerForm.name" />
        </NFormItem>
        <NFormItem :label="$t('page.system.role.form.code')" path="code">
          <NInput v-model:value="drawerForm.code" />
        </NFormItem>
        <NFormItem :label="$t('page.system.role.form.dataScope')" path="data_scope">
          <NSelect v-model:value="drawerForm.data_scope" :options="dataScopeOptions" />
        </NFormItem>
        <NFormItem :label="$t('page.system.role.form.status')" path="status">
          <NRadioGroup v-model:value="drawerForm.status">
            <NRadio value="1">正常</NRadio>
            <NRadio value="0">停用</NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.role.form.menus')" path="menuIds">
          <NTreeSelect
            v-model:value="drawerForm.menuIds"
            :options="menuTree"
            key-field="id"
            label-field="title"
            children-field="children"
            multiple
            cascade
            clearable
          />
        </NFormItem>
        <NFormItem
          v-if="drawerForm.data_scope === '2'"
          :label="$t('page.system.role.form.departments')"
          path="departmentIds"
        >
          <NTreeSelect
            v-model:value="drawerForm.departmentIds"
            :options="deptTree"
            key-field="id"
            label-field="name"
            children-field="children"
            multiple
            cascade
            clearable
          />
        </NFormItem>
        <NFormItem :label="$t('page.system.role.form.remark')" path="remark">
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

  <NModal v-model:show="assignMenusVisible" preset="card" title="分配菜单" style="width: 600px">
    <NTreeSelect
      v-model:value="assignMenusSelected"
      :options="menuTree"
      key-field="id"
      label-field="title"
      children-field="children"
      multiple
      cascade
      clearable
    />
    <template #footer>
      <NSpace justify="end">
        <NButton @click="assignMenusVisible = false">{{ $t('common.cancel') }}</NButton>
        <NButton type="primary" :loading="loading" @click="onAssignMenusSubmit">{{
          $t('common.confirm')
        }}</NButton>
      </NSpace>
    </template>
  </NModal>
</template>
