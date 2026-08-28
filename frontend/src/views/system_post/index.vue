<script setup lang="ts">
import { computed, h, reactive, ref, watch } from 'vue';
import { NTag, useMessage, useDialog, type FormInst, type FormRules } from 'naive-ui';
import type { FlatResponseData } from '@sa/axios';
import { $t } from '@/locales';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { postApi } from '@/service/api';

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
  status: '1' | '0';
  sort_order: number;
  remark: string;
}>({
  name: '',
  code: '',
  status: '1',
  sort_order: 0,
  remark: ''
});

const drawerRules = computed<FormRules>(() => ({
  name: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  code: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  status: [{ required: true, message: $t('form.required'), trigger: 'change' }]
}));

type Row = Api.System.Post;
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
      status: queryForm.status || undefined
    };
    return postApi.list(params);
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
    { title: $t('page.system.post.form.name'), key: 'name', width: 180 },
    { title: $t('page.system.post.form.code'), key: 'code', width: 180 },
    {
      title: $t('page.system.post.form.status'),
      key: 'status',
      width: 100,
      render: row =>
        h(
          NTag,
          { size: 'small', type: row.status === '1' ? 'success' : 'error' },
          {
            default: () => (row.status === '1' ? $t('page.system.common.enabled') : $t('page.system.common.disabled'))
          }
        )
    },
    { title: $t('page.system.post.form.sortOrder'), key: 'sort_order', width: 100 },
    { title: $t('page.system.post.form.remark'), key: 'remark', width: 200 },
    { title: $t('page.system.common.createdAt'), key: 'created_at', width: 180 },
    {
      title: $t('common.operate'),
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: row =>
        h('div', { style: { display: 'flex', gap: '8px' } }, [createButtonEdit(row), createButtonDelete(row)])
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

watch(
  editingData,
  v => {
    if (v) {
      Object.assign(drawerForm, {
        name: v.name || '',
        code: v.code || '',
        status: v.status || '1',
        sort_order: v.sort_order || 0,
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
    status: '1' as const,
    sort_order: 0,
    remark: ''
  };
}

async function onSubmit() {
  const valid = await drawerFormRef.value?.validate().catch(() => false);
  if (!valid) {
    message.warning($t('common.pleaseCheckValue'));
    return;
  }
  const payload = { ...drawerForm };
  const { error } =
    operateType.value === 'add'
      ? await postApi.add(payload)
      : await postApi.update(editingData.value!.id, payload);
  if (error) return;
  message.success(operateType.value === 'add' ? $t('common.addSuccess') : $t('common.modifySuccess'));
  closeDrawer();
  await getData();
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
        const { error } = await postApi.remove(row.id);
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
      const { error } = await postApi.batchDelete(ids);
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
    status: ''
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
          <NFormItem :label="$t('page.system.post.form.status')">
            <NSelect
              v-model:value="queryForm.status"
              :options="[
                { label: $t('page.system.common.enabled'), value: '1' },
                { label: $t('page.system.common.disabled'), value: '0' }
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
          v-model:checked-row-keys="checkedRowKeys"
          :columns="columns"
          :data="data"
          :loading="loading"
          :pagination="mobilePagination"
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
          <NFormItem :label="$t('page.system.post.form.name')" path="name">
            <NInput v-model:value="drawerForm.name" />
          </NFormItem>
          <NFormItem :label="$t('page.system.post.form.code')" path="code">
            <NInput v-model:value="drawerForm.code" />
          </NFormItem>
          <NFormItem :label="$t('page.system.post.form.status')" path="status">
            <NRadioGroup v-model:value="drawerForm.status">
              <NRadio value="1">{{ $t('page.system.common.enabled') }}</NRadio>
              <NRadio value="0">{{ $t('page.system.common.disabled') }}</NRadio>
            </NRadioGroup>
          </NFormItem>
          <NFormItem :label="$t('page.system.post.form.sortOrder')" path="sort_order">
            <NInputNumber v-model:value="drawerForm.sort_order" :min="0" />
          </NFormItem>
          <NFormItem :label="$t('page.system.post.form.remark')" path="remark">
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
