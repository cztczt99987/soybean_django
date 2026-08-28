<script setup lang="ts">
import { computed, h, reactive, ref, watch } from 'vue';
import { useMessage, useDialog, type FormInst, type FormRules } from 'naive-ui';
import { $t } from '@/locales';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { dictTypeApi, dictDataApi } from '@/service/api';

const message = useMessage();
const dialog = useDialog();

const activeTab = ref<'type' | 'data'>('type');

const dictTypeOptions = ref<{ id: number; name: string; code: string }[]>([]);
async function loadDictTypeOptions() {
  const { data, error } = await dictTypeApi.options();
  if (!error) dictTypeOptions.value = data || [];
}
loadDictTypeOptions();

/* ============ 字典类型 Tab ============ */

const typeFormRef = ref<FormInst | null>(null);
const typeQueryForm = reactive<{
  keyword: string;
  status: '' | '1' | '0';
}>({
  keyword: '',
  status: ''
});

const typeDrawerFormRef = ref<FormInst | null>(null);
const typeDrawerForm = reactive<{
  name: string;
  code: string;
  status: '1' | '0';
  remark: string;
}>({
  name: '',
  code: '',
  status: '1',
  remark: ''
});

const typeDrawerRules = computed<FormRules>(() => ({
  name: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  code: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  status: [{ required: true, message: $t('form.required'), trigger: 'change' }]
}));

let typeTbl: any;
typeTbl = useNaivePaginatedTable({
  api: () => {
    const page = typeTbl?.pagination?.page ?? 1;
    const pageSize = typeTbl?.pagination?.pageSize ?? 10;
    const params: any = { current: page, size: pageSize };
    Object.entries(typeQueryForm).forEach(([k, v]) => {
      if (v !== '' && v !== null && v !== undefined) params[k] = v;
    });
    return dictTypeApi.list(params);
  },
  columns: () => [
    { type: 'selection', width: 60 },
    {
      title: '#',
      key: '__index__',
      width: 64,
      render: (...args: any[]): any => {
        const index = args.length >= 3 ? args[2] : args[1];
        return ((typeTbl?.pagination?.page ?? 1) - 1) * (typeTbl?.pagination?.pageSize ?? 10) + index + 1;
      }
    },
    { title: 'ID', key: 'id', width: 80 },
    { title: $t('page.system.dict.form.name'), key: 'name', width: 180 },
    { title: $t('page.system.dict.form.code'), key: 'code', width: 180 },
    {
      title: $t('page.system.dict.form.status'),
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
    { title: $t('page.system.dict.form.remark'), key: 'remark', width: 200 },
    { title: '创建时间', key: 'created_at', width: 180 },
    {
      title: $t('common.operate'),
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (row: any): any =>
        h('div', { style: { display: 'flex', gap: '8px' } }, [
          createTypeButtonEdit(row),
          createTypeButtonDelete(row)
        ])
    }
  ],
  transform: defaultTransform as any
} as any);

const typeLoading = typeTbl.loading;
const typeData = typeTbl.data;
const typeColumns = typeTbl.columns;
const typeColumnChecks = typeTbl.columnChecks;
const typeGetData = typeTbl.getData;
const typePagination = typeTbl.pagination;
const typeMobilePagination = typeTbl.mobilePagination;

const typeOps: any = (useTableOperate as any)(typeData, 'id', typeGetData);
const typeDrawerVisible = typeOps.drawerVisible;
const typeOpenDrawer = typeOps.openDrawer;
const typeCloseDrawer = typeOps.closeDrawer;
const typeOperateType = typeOps.operateType;
const typeHandleAdd = typeOps.handleAdd;
const typeEditingData = typeOps.editingData;
const typeHandleEdit = typeOps.handleEdit;
const typeCheckedRowKeys = typeOps.checkedRowKeys;
const typeOnBatchDeleted = typeOps.onBatchDeleted;
const typeOnDeleted = typeOps.onDeleted;

watch(
  typeEditingData,
  (v: any) => {
    if (v) {
      Object.assign(typeDrawerForm, {
        name: v.name || '',
        code: v.code || '',
        status: v.status || '1',
        remark: v.remark || ''
      });
    } else {
      Object.assign(typeDrawerForm, typeDefaultForm());
    }
  },
  { immediate: true }
);

function typeDefaultForm() {
  return {
    name: '',
    code: '',
    status: '1' as const,
    remark: ''
  };
}

async function onTypeSubmit() {
  const valid = await typeDrawerFormRef.value?.validate().catch(() => false);
  if (!valid) {
    message.warning($t('common.pleaseCheckValue'));
    return;
  }
  const payload: any = { ...typeDrawerForm };
  const { error } =
    typeOperateType.value === 'add'
      ? await dictTypeApi.add(payload)
      : await dictTypeApi.update(typeEditingData.value!.id, payload);
  if (error) return;
  message.success(typeOperateType.value === 'add' ? $t('common.addSuccess') : $t('common.modifySuccess'));
  typeCloseDrawer();
  await typeGetData();
  await loadDictTypeOptions();
}

function createTypeButtonEdit(row: any): any {
  return h(
    'NButton',
    {
      size: 'small',
      type: 'primary',
      ghost: true,
      onClick: () => typeHandleEdit(row.id)
    },
    { default: () => $t('common.edit') }
  );
}

function createTypeButtonDelete(row: any): any {
  return h(
    'NPopconfirm',
    {
      onPositiveClick: async () => {
        const { error } = await dictTypeApi.remove(row.id);
        if (!error) {
          typeOnDeleted();
          await loadDictTypeOptions();
        }
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

async function onTypeBatchDelete() {
  if (!typeCheckedRowKeys.value.length) return;
  dialog.warning({
    title: $t('common.warning'),
    content: $t('common.confirmDelete'),
    positiveText: $t('common.confirm'),
    negativeText: $t('common.cancel'),
    onPositiveClick: async () => {
      const ids = typeCheckedRowKeys.value.map(Number);
      const { error } = await dictTypeApi.batchDelete(ids);
      if (!error) {
        typeOnBatchDeleted();
        await loadDictTypeOptions();
      }
    }
  });
}

function onTypeSearch() {
  typePagination.page = 1;
  typeGetData();
}
function onTypeReset() {
  Object.assign(typeQueryForm, {
    keyword: '',
    status: ''
  });
  onTypeSearch();
}

/* ============ 字典数据 Tab ============ */

const dataFormRef = ref<FormInst | null>(null);
const selectedDictTypeId = ref<number | null>(null);
const dataQueryForm = reactive<{
  keyword: string;
  status: '' | '1' | '0';
}>({
  keyword: '',
  status: ''
});

const dataDrawerFormRef = ref<FormInst | null>(null);
const dataDrawerForm = reactive<{
  dictCode: string;
  label: string;
  value: string;
  css_class: string;
  list_class: string;
  is_default: boolean;
  status: '1' | '0';
  remark: string;
}>({
  dictCode: '',
  label: '',
  value: '',
  css_class: '',
  list_class: '',
  is_default: false,
  status: '1',
  remark: ''
});

const dataDrawerRules = computed<FormRules>(() => ({
  dictCode: [{ required: true, message: $t('form.required'), trigger: 'change' }],
  label: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  value: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  status: [{ required: true, message: $t('form.required'), trigger: 'change' }]
}));

let dataTbl: any;
dataTbl = useNaivePaginatedTable({
  api: () => {
    const page = dataTbl?.pagination?.page ?? 1;
    const pageSize = dataTbl?.pagination?.pageSize ?? 10;
    const params: any = { current: page, size: pageSize };
    Object.entries(dataQueryForm).forEach(([k, v]) => {
      if (v !== '' && v !== null && v !== undefined) params[k] = v;
    });
    const selectedType = dictTypeOptions.value.find(t => t.id === selectedDictTypeId.value);
    if (selectedType) {
      params.dictCode = selectedType.code;
    }
    return dictDataApi.list(params);
  },
  columns: () => [
    { type: 'selection', width: 60 },
    {
      title: '#',
      key: '__index__',
      width: 64,
      render: (...args: any[]): any => {
        const index = args.length >= 3 ? args[2] : args[1];
        return ((dataTbl?.pagination?.page ?? 1) - 1) * (dataTbl?.pagination?.pageSize ?? 10) + index + 1;
      }
    },
    { title: 'ID', key: 'id', width: 80 },
    { title: $t('page.system.dict.data.label'), key: 'label', width: 160 },
    { title: $t('page.system.dict.data.value'), key: 'value', width: 160 },
    { title: $t('page.system.dict.data.cssClass'), key: 'css_class', width: 120 },
    { title: $t('page.system.dict.data.listClass'), key: 'list_class', width: 120 },
    {
      title: $t('page.system.dict.data.isDefault'),
      key: 'is_default',
      width: 100,
      render: (row: any) => (row.is_default ? '是' : '否')
    },
    {
      title: $t('page.system.dict.data.status'),
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
    { title: $t('page.system.dict.data.remark'), key: 'remark', width: 200 },
    { title: '创建时间', key: 'created_at', width: 180 },
    {
      title: $t('common.operate'),
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (row: any): any =>
        h('div', { style: { display: 'flex', gap: '8px' } }, [
          createDataButtonEdit(row),
          createDataButtonDelete(row)
        ])
    }
  ],
  transform: defaultTransform as any
} as any);

const dataLoading = dataTbl.loading;
const dataData = dataTbl.data;
const dataColumns = dataTbl.columns;
const dataColumnChecks = dataTbl.columnChecks;
const dataGetData = dataTbl.getData;
const dataPagination = dataTbl.pagination;
const dataMobilePagination = dataTbl.mobilePagination;

const dataOps: any = (useTableOperate as any)(dataData, 'id', dataGetData);
const dataDrawerVisible = dataOps.drawerVisible;
const dataOpenDrawer = dataOps.openDrawer;
const dataCloseDrawer = dataOps.closeDrawer;
const dataOperateType = dataOps.operateType;
const dataHandleAdd = dataOps.handleAdd;
const dataEditingData = dataOps.editingData;
const dataHandleEdit = dataOps.handleEdit;
const dataCheckedRowKeys = dataOps.checkedRowKeys;
const dataOnBatchDeleted = dataOps.onBatchDeleted;
const dataOnDeleted = dataOps.onDeleted;

watch(
  dataEditingData,
  (v: any) => {
    if (v) {
      Object.assign(dataDrawerForm, {
        dictCode: v.dictCode || '',
        label: v.label || '',
        value: v.value || '',
        css_class: v.css_class || '',
        list_class: v.list_class || '',
        is_default: v.is_default || false,
        status: v.status || '1',
        remark: v.remark || ''
      });
    } else {
      const selectedType = dictTypeOptions.value.find(t => t.id === selectedDictTypeId.value);
      Object.assign(dataDrawerForm, {
        ...dataDefaultForm(),
        dictCode: selectedType?.code || ''
      });
    }
  },
  { immediate: true }
);

function dataDefaultForm() {
  return {
    dictCode: '',
    label: '',
    value: '',
    css_class: '',
    list_class: '',
    is_default: false,
    status: '1' as const,
    remark: ''
  };
}

async function onDataSubmit() {
  const valid = await dataDrawerFormRef.value?.validate().catch(() => false);
  if (!valid) {
    message.warning($t('common.pleaseCheckValue'));
    return;
  }
  const payload: any = { ...dataDrawerForm };
  const { error } =
    dataOperateType.value === 'add'
      ? await dictDataApi.add(payload)
      : await dictDataApi.update(dataEditingData.value!.id, payload);
  if (error) return;
  message.success(dataOperateType.value === 'add' ? $t('common.addSuccess') : $t('common.modifySuccess'));
  dataCloseDrawer();
  await dataGetData();
}

function createDataButtonEdit(row: any): any {
  return h(
    'NButton',
    {
      size: 'small',
      type: 'primary',
      ghost: true,
      onClick: () => dataHandleEdit(row.id)
    },
    { default: () => $t('common.edit') }
  );
}

function createDataButtonDelete(row: any): any {
  return h(
    'NPopconfirm',
    {
      onPositiveClick: async () => {
        const { error } = await dictDataApi.remove(row.id);
        if (!error) dataOnDeleted();
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

async function onDataBatchDelete() {
  if (!dataCheckedRowKeys.value.length) return;
  dialog.warning({
    title: $t('common.warning'),
    content: $t('common.confirmDelete'),
    positiveText: $t('common.confirm'),
    negativeText: $t('common.cancel'),
    onPositiveClick: async () => {
      const ids = dataCheckedRowKeys.value.map(Number);
      const { error } = await dictDataApi.batchDelete(ids);
      if (!error) dataOnBatchDeleted();
    }
  });
}

function onDataSearch() {
  dataPagination.page = 1;
  dataGetData();
}
function onDataReset() {
  Object.assign(dataQueryForm, {
    keyword: '',
    status: ''
  });
  onDataSearch();
}

watch(selectedDictTypeId, () => {
  if (selectedDictTypeId.value) {
    dataGetData();
  }
});

function handleDataAdd() {
  if (!selectedDictTypeId.value) {
    message.warning('请先选择字典类型');
    return;
  }
  dataHandleAdd();
}
</script>

<template>
  <NSpace vertical :size="12">
    <NTabs v-model:value="activeTab" type="line" animated>
      <NTabPane name="type" tab="字典类型">
        <NSpace vertical :size="12">
          <NCard>
            <NForm ref="typeFormRef" inline label-placement="left" label-width="auto" :model="typeQueryForm">
              <NFormItem :label="$t('common.keywordSearch')">
                <NInput
                  v-model:value="typeQueryForm.keyword"
                  clearable
                  :placeholder="$t('common.keywordSearch')"
                />
              </NFormItem>
              <NFormItem :label="$t('page.system.dict.form.status')">
                <NSelect
                  v-model:value="typeQueryForm.status"
                  :options="[
                    { label: '正常', value: '1' },
                    { label: '停用', value: '0' }
                  ]"
                  clearable
                />
              </NFormItem>
              <NFormItem>
                <NSpace>
                  <NButton type="primary" @click="onTypeSearch">
                    <template #icon><icon-mdi-magnify class="text-icon" /></template>{{ $t('common.search') }}
                  </NButton>
                  <NButton @click="onTypeReset">
                    <template #icon><icon-mdi-refresh class="text-icon" /></template>{{ $t('common.reset') }}
                  </NButton>
                </NSpace>
              </NFormItem>
            </NForm>
          </NCard>

          <NCard :bordered="false" class="!mt-0">
            <TableHeaderOperation
              v-model:columns="typeColumnChecks"
              :loading="typeLoading"
              :disabled-delete="!typeCheckedRowKeys.length"
              @add="typeHandleAdd"
              @delete="onTypeBatchDelete"
              @refresh="typeGetData"
            />

            <NDataTable
              :columns="typeColumns"
              :data="typeData"
              :loading="typeLoading"
              :pagination="typeMobilePagination"
              v-model:checked-row-keys="typeCheckedRowKeys"
              :scroll-x="1500"
              :bordered="false"
              striped
            />
          </NCard>
        </NSpace>
      </NTabPane>

      <NTabPane name="data" tab="字典数据">
        <NSpace vertical :size="12">
          <NCard>
            <NForm inline label-placement="left" label-width="auto">
              <NFormItem label="字典类型" required>
                <NSelect
                  v-model:value="selectedDictTypeId"
                  :options="dictTypeOptions.map(t => ({ label: t.name, value: t.id }))"
                  placeholder="请选择字典类型"
                  clearable
                />
              </NFormItem>
            </NForm>
          </NCard>

          <NCard>
            <NForm ref="dataFormRef" inline label-placement="left" label-width="auto" :model="dataQueryForm">
              <NFormItem :label="$t('common.keywordSearch')">
                <NInput
                  v-model:value="dataQueryForm.keyword"
                  clearable
                  :placeholder="$t('common.keywordSearch')"
                />
              </NFormItem>
              <NFormItem :label="$t('page.system.dict.data.status')">
                <NSelect
                  v-model:value="dataQueryForm.status"
                  :options="[
                    { label: '正常', value: '1' },
                    { label: '停用', value: '0' }
                  ]"
                  clearable
                />
              </NFormItem>
              <NFormItem>
                <NSpace>
                  <NButton type="primary" @click="onDataSearch" :disabled="!selectedDictTypeId">
                    <template #icon><icon-mdi-magnify class="text-icon" /></template>{{ $t('common.search') }}
                  </NButton>
                  <NButton @click="onDataReset">
                    <template #icon><icon-mdi-refresh class="text-icon" /></template>{{ $t('common.reset') }}
                  </NButton>
                </NSpace>
              </NFormItem>
            </NForm>
          </NCard>

          <NCard :bordered="false" class="!mt-0">
            <TableHeaderOperation
              v-model:columns="dataColumnChecks"
              :loading="dataLoading"
              :disabled-delete="!dataCheckedRowKeys.length || !selectedDictTypeId"
              @add="handleDataAdd"
              @delete="onDataBatchDelete"
              @refresh="dataGetData"
            />

            <NDataTable
              :columns="dataColumns"
              :data="dataData"
              :loading="dataLoading"
              :pagination="dataMobilePagination"
              v-model:checked-row-keys="dataCheckedRowKeys"
              :scroll-x="1700"
              :bordered="false"
              striped
            />
          </NCard>
        </NSpace>
      </NTabPane>
    </NTabs>
  </NSpace>

  <!-- 字典类型 抽屉 -->
  <NDrawer v-model:show="typeDrawerVisible" :width="640" placement="right" :mask-closable="false">
    <NDrawerContent
      :title="typeOperateType === 'add' ? $t('common.add') : $t('common.edit')"
      :closable="true"
    >
      <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
        <NButton size="small" @click="typeCloseDrawer">{{ $t('common.close') }}</NButton>
      </div>
      <NForm ref="typeDrawerFormRef" label-placement="top" :model="typeDrawerForm" :rules="typeDrawerRules">
        <NFormItem :label="$t('page.system.dict.form.name')" path="name">
          <NInput v-model:value="typeDrawerForm.name" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.form.code')" path="code">
          <NInput v-model:value="typeDrawerForm.code" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.form.status')" path="status">
          <NRadioGroup v-model:value="typeDrawerForm.status">
            <NRadio value="1">正常</NRadio>
            <NRadio value="0">停用</NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.form.remark')" path="remark">
          <NInput v-model:value="typeDrawerForm.remark" type="textarea" :rows="3" />
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace justify="end">
          <NButton @click="typeCloseDrawer">{{ $t('common.cancel') }}</NButton>
          <NButton type="primary" :loading="typeLoading" @click="onTypeSubmit">{{ $t('common.confirm') }}</NButton>
        </NSpace>
      </template>
    </NDrawerContent>
  </NDrawer>

  <!-- 字典数据 抽屉 -->
  <NDrawer v-model:show="dataDrawerVisible" :width="640" placement="right" :mask-closable="false">
    <NDrawerContent
      :title="dataOperateType === 'add' ? $t('common.add') : $t('common.edit')"
      :closable="true"
    >
      <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
        <NButton size="small" @click="dataCloseDrawer">{{ $t('common.close') }}</NButton>
      </div>
      <NForm ref="dataDrawerFormRef" label-placement="top" :model="dataDrawerForm" :rules="dataDrawerRules">
        <NFormItem label="字典编码" path="dictCode">
          <NSelect
            v-model:value="dataDrawerForm.dictCode"
            :options="dictTypeOptions.map(t => ({ label: t.name, value: t.code }))"
          />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.label')" path="label">
          <NInput v-model:value="dataDrawerForm.label" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.value')" path="value">
          <NInput v-model:value="dataDrawerForm.value" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.cssClass')" path="css_class">
          <NInput v-model:value="dataDrawerForm.css_class" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.listClass')" path="list_class">
          <NInput v-model:value="dataDrawerForm.list_class" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.isDefault')" path="is_default">
          <NSwitch v-model:value="dataDrawerForm.is_default" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.status')" path="status">
          <NRadioGroup v-model:value="dataDrawerForm.status">
            <NRadio value="1">正常</NRadio>
            <NRadio value="0">停用</NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.remark')" path="remark">
          <NInput v-model:value="dataDrawerForm.remark" type="textarea" :rows="3" />
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace justify="end">
          <NButton @click="dataCloseDrawer">{{ $t('common.cancel') }}</NButton>
          <NButton type="primary" :loading="dataLoading" @click="onDataSubmit">{{ $t('common.confirm') }}</NButton>
        </NSpace>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>
