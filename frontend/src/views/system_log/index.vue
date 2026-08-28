<script setup lang="ts">
import { h, reactive, ref } from 'vue';
import { useMessage, useDialog, type FormInst } from 'naive-ui';
import { $t } from '@/locales';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { logApi } from '@/service/api';

const message = useMessage();
const dialog = useDialog();

const formRef = ref<FormInst | null>(null);
const queryForm = reactive<{
  keyword: string;
  operationType: '' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9';
  status: '' | '1' | '0';
  beginTime: string | null;
  endTime: string | null;
  dateRange: [string, string] | null;
}>({
  keyword: '',
  operationType: '',
  status: '',
  beginTime: null,
  endTime: null,
  dateRange: null
});

const cleanDays = ref<number>(30);
const cleanDialogVisible = ref(false);

const operationTypeOptions = [
  { label: '新增', value: '1' },
  { label: '修改', value: '2' },
  { label: '删除', value: '3' },
  { label: '查询', value: '4' },
  { label: '导出', value: '5' },
  { label: '导入', value: '6' },
  { label: '登录', value: '7' },
  { label: '登出', value: '8' },
  { label: '其他', value: '9' }
];

let tbl: any;
tbl = useNaivePaginatedTable({
  api: () => {
    const page = tbl?.pagination?.page ?? 1;
    const pageSize = tbl?.pagination?.pageSize ?? 10;
    const params: any = { current: page, size: pageSize };
    Object.entries(queryForm).forEach(([k, v]) => {
      if (k === 'dateRange') return;
      if (v !== '' && v !== null && v !== undefined) params[k] = v;
    });
    if (queryForm.dateRange && queryForm.dateRange.length === 2) {
      params.beginTime = queryForm.dateRange[0];
      params.endTime = queryForm.dateRange[1];
    }
    return logApi.list(params);
  },
  columns: () => [
    { type: 'selection', width: 60 },
    {
      title: '#',
      key: '__index__',
      width: 64,
      render: (...args: any[]): any => {
        const index = args.length >= 3 ? args[2] : args[1];
        return ((tbl?.pagination?.page ?? 1) - 1) * (tbl?.pagination?.pageSize ?? 10) + index + 1;
      }
    },
    { title: $t('page.system.log.fields.username'), key: 'username', width: 120 },
    { title: $t('page.system.log.fields.module'), key: 'module', width: 120 },
    { title: $t('page.system.log.fields.description'), key: 'description', width: 180 },
    {
      title: $t('page.system.log.fields.operationType'),
      key: 'operation_type',
      width: 100,
      render: (row: any) => operationTypeOptions.find(o => o.value === row.operation_type)?.label || '-'
    },
    { title: $t('page.system.log.fields.method'), key: 'method', width: 100 },
    { title: $t('page.system.log.fields.url'), key: 'request_url', width: 240, ellipsis: { tooltip: true } },
    { title: $t('page.system.log.fields.ip'), key: 'ip', width: 140 },
    {
      title: $t('page.system.log.fields.status'),
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
          row.status === '1' ? '成功' : '失败'
        )
    },
    {
      title: $t('page.system.log.fields.costTime'),
      key: 'cost_time',
      width: 100,
      render: (row: any) => `${row.cost_time} ms`
    },
    { title: $t('page.system.log.fields.operatedAt'), key: 'operated_at', width: 180 },
    {
      title: $t('common.operate'),
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (row: any): any =>
        h('div', { style: { display: 'flex', gap: '8px' } }, [createButtonDelete(row)])
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
const checkedRowKeys = ops.checkedRowKeys;
const onBatchDeleted = ops.onBatchDeleted;
const onDeleted = ops.onDeleted;

function createButtonDelete(row: any): any {
  return h(
    'NPopconfirm',
    {
      onPositiveClick: async () => {
        const { error } = await logApi.remove(row.id);
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
      const { error } = await logApi.batchDelete(ids);
      if (!error) onBatchDeleted();
    }
  });
}

function openCleanDialog() {
  cleanDays.value = 30;
  cleanDialogVisible.value = true;
}

async function onCleanSubmit() {
  const { error } = await logApi.clean(cleanDays.value);
  if (!error) {
    message.success(`已清理 ${cleanDays.value} 天前的日志`);
    cleanDialogVisible.value = false;
    await getData();
  }
}

function onSearch() {
  pagination.page = 1;
  getData();
}
function onReset() {
  Object.assign(queryForm, {
    keyword: '',
    operationType: '',
    status: '',
    beginTime: null,
    endTime: null,
    dateRange: null
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
        <NFormItem :label="$t('page.system.log.fields.operationType')">
          <NSelect
            v-model:value="queryForm.operationType"
            :options="operationTypeOptions"
            clearable
          />
        </NFormItem>
        <NFormItem :label="$t('page.system.log.fields.status')">
          <NSelect
            v-model:value="queryForm.status"
            :options="[
              { label: '成功', value: '1' },
              { label: '失败', value: '0' }
            ]"
            clearable
          />
        </NFormItem>
        <NFormItem label="时间范围">
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
        @delete="onBatchDelete"
        @refresh="getData"
      >
        <template #prefix>
          <NButton size="small" ghost type="warning" @click="openCleanDialog">
            <template #icon>
              <icon-mdi-broom class="text-icon" />
            </template>
            {{ $t('page.system.log.action.clean') }}
          </NButton>
        </template>
        <template #default></template>
      </TableHeaderOperation>

      <NDataTable
        :columns="columns"
        :data="data"
        :loading="loading"
        :pagination="mobilePagination"
        v-model:checked-row-keys="checkedRowKeys"
        :scroll-x="1900"
        :bordered="false"
        striped
      />
    </NCard>
  </NSpace>

  <NModal v-model:show="cleanDialogVisible" preset="card" title="清理日志" style="width: 420px">
    <NForm label-placement="top">
      <NFormItem label="清理多少天前的日志">
        <NInputNumber v-model:value="cleanDays" :min="1" :max="3650" />
      </NFormItem>
    </NForm>
    <template #footer>
      <NSpace justify="end">
        <NButton @click="cleanDialogVisible = false">{{ $t('common.cancel') }}</NButton>
        <NButton type="primary" :loading="loading" @click="onCleanSubmit">{{ $t('common.confirm') }}</NButton>
      </NSpace>
    </template>
  </NModal>
</template>
