<script setup lang="ts">
import { computed, h, reactive, ref } from 'vue';
import { NTag, useDialog, useMessage, type FormInst } from 'naive-ui';
import type { FlatResponseData } from '@sa/axios';
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

const operationTypeOptions = computed(() => [
  { label: $t('page.system.common.operationType.other'), value: '1' },
  { label: $t('page.system.common.operationType.create'), value: '2' },
  { label: $t('page.system.common.operationType.update'), value: '3' },
  { label: $t('page.system.common.operationType.remove'), value: '4' },
  { label: $t('page.system.common.operationType.grant'), value: '5' },
  { label: $t('page.system.common.operationType.export'), value: '6' },
  { label: $t('page.system.common.operationType.import'), value: '7' },
  { label: $t('page.system.common.operationType.login'), value: '8' },
  { label: $t('page.system.common.operationType.logout'), value: '9' }
]);

const logStatusOptions = computed(() => [
  { label: $t('page.system.common.success'), value: '1' },
  { label: $t('page.system.common.failure'), value: '0' }
]);

type Row = Api.System.OperationLog;
type Resp = FlatResponseData<App.Service.Response<unknown>, Api.System.ListResp<Row>>;
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
      operationType: queryForm.operationType || undefined,
      status: queryForm.status || undefined
    };
    if (queryForm.dateRange && queryForm.dateRange.length === 2) {
      params.beginTime = queryForm.dateRange[0];
      params.endTime = queryForm.dateRange[1];
    }
    return logApi.list(params);
  },
  columns: () => [
    { type: 'selection', width: 60 },
    {
      title: $t('common.index'),
      key: '__index__',
      width: 64,
      render: (_row, rowIndex) => ((tbl?.pagination?.page ?? 1) - 1) * (tbl?.pagination?.pageSize ?? 10) + rowIndex + 1
    },
    { title: $t('page.system.log.fields.username'), key: 'username', width: 120 },
    { title: $t('page.system.log.fields.module'), key: 'module', width: 120 },
    { title: $t('page.system.log.fields.description'), key: 'description', width: 180 },
    {
      title: $t('page.system.log.fields.operationType'),
      key: 'operation_type',
      width: 100,
      render: row => operationTypeOptions.value.find(o => o.value === row.operation_type)?.label || '-'
    },
    { title: $t('page.system.log.fields.method'), key: 'method', width: 100 },
    { title: $t('page.system.log.fields.url'), key: 'request_url', width: 240, ellipsis: { tooltip: true } },
    { title: $t('page.system.log.fields.ip'), key: 'ip', width: 140 },
    {
      title: $t('page.system.log.fields.status'),
      key: 'status',
      width: 100,
      render: row =>
        h(
          NTag,
          { size: 'small', type: row.status === '1' ? 'success' : 'error' },
          {
            default: () => (row.status === '1' ? $t('page.system.common.success') : $t('page.system.common.failure'))
          }
        )
    },
    {
      title: $t('page.system.log.fields.costTime'),
      key: 'cost_time',
      width: 100,
      render: row => `${row.cost_time} ms`
    },
    { title: $t('page.system.log.fields.operatedAt'), key: 'operated_at', width: 180 },
    {
      title: $t('common.operate'),
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: row => h('div', { style: { display: 'flex', gap: '8px' } }, [createButtonDelete(row)])
    }
  ],
  transform: defaultTransform
});

const { data, loading, columns, columnChecks, getData, getDataByPage, mobilePagination } = tbl;

const { checkedRowKeys, onBatchDeleted, onDeleted } = useTableOperate(data, 'id', getData);

function createButtonDelete(row: Row) {
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
    message.success($t('page.system.common.cleanSuccess'));
    cleanDialogVisible.value = false;
    await getData();
  }
}

function onSearch() {
  getDataByPage();
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
  getDataByPage();
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
              :options="logStatusOptions"
              clearable
            />
          </NFormItem>
          <NFormItem :label="$t('page.system.log.fields.dateRange')">
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
          v-model:checked-row-keys="checkedRowKeys"
          :columns="columns"
          :data="data"
          :loading="loading"
          :pagination="mobilePagination"
          :scroll-x="1900"
          :bordered="false"
          striped
        />
      </NCard>
    </NSpace>

    <NModal v-model:show="cleanDialogVisible" preset="card" :title="$t('page.system.log.action.cleanTitle')" style="width: 420px">
      <NForm label-placement="top">
        <NFormItem :label="$t('page.system.log.action.cleanDays')">
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
  </div>
</template>
