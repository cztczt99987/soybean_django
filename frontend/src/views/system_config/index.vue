<script setup lang="ts">
import { computed, h, reactive, ref, watch } from 'vue';
import { useMessage, useDialog, type FormInst, type FormRules } from 'naive-ui';
import { $t } from '@/locales';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { configApi } from '@/service/api';

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
  value: string;
  value_type: 'S' | 'N' | 'B' | 'J';
  is_system: boolean;
  status: '1' | '0';
  remark: string;
}>({
  name: '',
  code: '',
  value: '',
  value_type: 'S',
  is_system: false,
  status: '1',
  remark: ''
});

const valueTypeOptions = [
  { label: '字符串', value: 'S' },
  { label: '数字', value: 'N' },
  { label: '布尔', value: 'B' },
  { label: 'JSON', value: 'J' }
];

const drawerRules = computed<FormRules>(() => ({
  name: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  code: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  value: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  value_type: [{ required: true, message: $t('form.required'), trigger: 'change' }],
  status: [{ required: true, message: $t('form.required'), trigger: 'change' }]
}));

const tbl: any = useNaivePaginatedTable({
  api: () => {
    const params: any = { current: tbl.pagination.page, size: tbl.pagination.pageSize };
    Object.entries(queryForm).forEach(([k, v]) => {
      if (v !== '' && v !== null && v !== undefined) params[k] = v;
    });
    return configApi.list(params);
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
    { title: $t('page.system.config.form.name'), key: 'name', width: 180 },
    { title: $t('page.system.config.form.code'), key: 'code', width: 180 },
    { title: $t('page.system.config.form.value'), key: 'value', width: 200 },
    {
      title: $t('page.system.config.form.valueType'),
      key: 'value_type',
      width: 100,
      render: (row: any) => valueTypeOptions.find(o => o.value === row.value_type)?.label || '-'
    },
    {
      title: $t('page.system.config.form.isSystem'),
      key: 'is_system',
      width: 100,
      render: (row: any) => (row.is_system ? '是' : '否')
    },
    {
      title: $t('page.system.config.form.status'),
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
    { title: $t('page.system.config.form.remark'), key: 'remark', width: 200 },
    { title: '创建时间', key: 'created_at', width: 180 },
    {
      title: $t('common.operate'),
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (row: any): any =>
        h('div', { style: { display: 'flex', gap: '8px' } }, [
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
        value: v.value || '',
        value_type: v.value_type || 'S',
        is_system: v.is_system || false,
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
    name: '',
    code: '',
    value: '',
    value_type: 'S' as const,
    is_system: false,
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
  const payload: any = { ...drawerForm };
  const { error } =
    operateType.value === 'add'
      ? await configApi.add(payload)
      : await configApi.update(editingData.value!.id, payload);
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
        const { error } = await configApi.remove(row.id);
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

async function onBatchDelete() {
  if (!checkedRowKeys.value.length) return;
  dialog.warning({
    title: $t('common.warning'),
    content: $t('common.confirmDelete'),
    positiveText: $t('common.confirm'),
    negativeText: $t('common.cancel'),
    onPositiveClick: async () => {
      const ids = checkedRowKeys.value.map(Number);
      const { error } = await configApi.batchDelete(ids);
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
        <NFormItem :label="$t('page.system.config.form.status')">
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
        <NFormItem :label="$t('page.system.config.form.name')" path="name">
          <NInput v-model:value="drawerForm.name" />
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.code')" path="code">
          <NInput v-model:value="drawerForm.code" />
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.value')" path="value">
          <NInput v-model:value="drawerForm.value" type="textarea" :rows="3" />
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.valueType')" path="value_type">
          <NSelect v-model:value="drawerForm.value_type" :options="valueTypeOptions" />
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.isSystem')" path="is_system">
          <NSwitch v-model:value="drawerForm.is_system" />
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.status')" path="status">
          <NRadioGroup v-model:value="drawerForm.status">
            <NRadio value="1">正常</NRadio>
            <NRadio value="0">停用</NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.remark')" path="remark">
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
</template>
