<script setup lang="ts">
import { computed, h, reactive, ref, watch } from 'vue';
import { NTag, useDialog, useMessage, type FormInst, type FormRules } from 'naive-ui';
import type { FlatResponseData } from '@sa/axios';
import { $t } from '@/locales';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { dictDataApi, dictTypeApi } from '@/service/api';

const message = useMessage();
const dialog = useDialog();

const activeTab = ref<'type' | 'data'>('type');

const dictTypeOptions = ref<{ id: number; name: string; code: string }[]>([]);
async function loadDictTypeOptions() {
  const { data, error } = await dictTypeApi.options();
  if (!error) dictTypeOptions.value = data || [];
}
loadDictTypeOptions();

const statusOptions = computed(() => [
  { label: $t('page.system.common.enabled'), value: '1' },
  { label: $t('page.system.common.disabled'), value: '0' }
]);

/* ============ 字典类型 Tab ============ */

type TypeRow = Api.System.DictType;
type TypeResp = FlatResponseData<App.Service.Response<unknown>, Api.System.ListResp<TypeRow>>;
type TypeTableInst = ReturnType<typeof useNaivePaginatedTable<TypeResp, TypeRow>>;

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

// 先声明为 undefined 再赋值：api 闭包首次同步调用时尚未就绪，需可选链兜底（不能改 const，否则 TDZ）
let typeTbl: TypeTableInst | undefined;
// eslint-disable-next-line prefer-const
typeTbl = useNaivePaginatedTable<TypeResp, TypeRow>({
  api: () => {
    const params: Api.System.SearchParams = {
      current: typeTbl?.pagination?.page ?? 1,
      size: typeTbl?.pagination?.pageSize ?? 10,
      keyword: typeQueryForm.keyword || undefined,
      status: typeQueryForm.status || undefined
    };
    return dictTypeApi.list(params);
  },
  columns: () => [
    { type: 'selection', width: 60 },
    {
      title: $t('common.index'),
      key: '__index__',
      width: 64,
      render: (_row, rowIndex) =>
        ((typeTbl?.pagination?.page ?? 1) - 1) * (typeTbl?.pagination?.pageSize ?? 10) + rowIndex + 1
    },
    { title: 'ID', key: 'id', width: 80 },
    { title: $t('page.system.dict.form.name'), key: 'name', width: 180 },
    { title: $t('page.system.dict.form.code'), key: 'code', width: 180 },
    {
      title: $t('page.system.dict.form.status'),
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
    { title: $t('page.system.dict.form.remark'), key: 'remark', width: 200 },
    { title: $t('page.system.common.createdAt'), key: 'created_at', width: 180 },
    {
      title: $t('common.operate'),
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: row =>
        h('div', { style: { display: 'flex', gap: '8px' } }, [
          createTypeButtonEdit(row),
          createTypeButtonDelete(row)
        ])
    }
  ],
  transform: defaultTransform
});

const {
  data: typeData,
  loading: typeLoading,
  columns: typeColumns,
  columnChecks: typeColumnChecks,
  getData: typeGetData,
  getDataByPage: typeGetDataByPage,
  mobilePagination: typeMobilePagination
} = typeTbl;

const {
  drawerVisible: typeDrawerVisible,
  closeDrawer: typeCloseDrawer,
  operateType: typeOperateType,
  handleAdd: typeHandleAdd,
  editingData: typeEditingData,
  handleEdit: typeHandleEdit,
  checkedRowKeys: typeCheckedRowKeys,
  onBatchDeleted: typeOnBatchDeleted,
  onDeleted: typeOnDeleted
} = useTableOperate(typeData, 'id', typeGetData);

watch(
  typeEditingData,
  v => {
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

function typeDefaultForm(): typeof typeDrawerForm {
  return {
    name: '',
    code: '',
    status: '1',
    remark: ''
  };
}

async function onTypeSubmit() {
  const valid = await typeDrawerFormRef.value?.validate().catch(() => false);
  if (!valid) {
    message.warning($t('common.pleaseCheckValue'));
    return;
  }
  const payload: Partial<TypeRow> = { ...typeDrawerForm };
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

function createTypeButtonEdit(row: TypeRow) {
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

function createTypeButtonDelete(row: TypeRow) {
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
  typeGetDataByPage();
}
function onTypeReset() {
  Object.assign(typeQueryForm, {
    keyword: '',
    status: ''
  });
  typeGetDataByPage();
}

/* ============ 字典数据 Tab ============ */

type DataRow = Api.System.DictData;
type DataResp = FlatResponseData<App.Service.Response<unknown>, Api.System.ListResp<DataRow>>;
type DataTableInst = ReturnType<typeof useNaivePaginatedTable<DataResp, DataRow>>;

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

// 先声明为 undefined 再赋值：api 闭包首次同步调用时尚未就绪，需可选链兜底（不能改 const，否则 TDZ）
let dataTbl: DataTableInst | undefined;
// eslint-disable-next-line prefer-const
dataTbl = useNaivePaginatedTable<DataResp, DataRow>({
  api: () => {
    const params: Api.System.SearchParams = {
      current: dataTbl?.pagination?.page ?? 1,
      size: dataTbl?.pagination?.pageSize ?? 10,
      keyword: dataQueryForm.keyword || undefined,
      status: dataQueryForm.status || undefined
    };
    const selectedType = dictTypeOptions.value.find(t => t.id === selectedDictTypeId.value);
    if (selectedType) {
      params.dictCode = selectedType.code;
    }
    return dictDataApi.list(params);
  },
  columns: () => [
    { type: 'selection', width: 60 },
    {
      title: $t('common.index'),
      key: '__index__',
      width: 64,
      render: (_row, rowIndex) =>
        ((dataTbl?.pagination?.page ?? 1) - 1) * (dataTbl?.pagination?.pageSize ?? 10) + rowIndex + 1
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
      render: row => (row.is_default ? $t('common.yesOrNo.yes') : $t('common.yesOrNo.no'))
    },
    {
      title: $t('page.system.dict.data.status'),
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
    { title: $t('page.system.dict.data.remark'), key: 'remark', width: 200 },
    { title: $t('page.system.common.createdAt'), key: 'created_at', width: 180 },
    {
      title: $t('common.operate'),
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: row =>
        h('div', { style: { display: 'flex', gap: '8px' } }, [
          createDataButtonEdit(row),
          createDataButtonDelete(row)
        ])
    }
  ],
  transform: defaultTransform
});

const {
  data: dataData,
  loading: dataLoading,
  columns: dataColumns,
  columnChecks: dataColumnChecks,
  getData: dataGetData,
  getDataByPage: dataGetDataByPage,
  mobilePagination: dataMobilePagination
} = dataTbl;

const {
  drawerVisible: dataDrawerVisible,
  closeDrawer: dataCloseDrawer,
  operateType: dataOperateType,
  handleAdd: dataHandleAdd,
  editingData: dataEditingData,
  handleEdit: dataHandleEdit,
  checkedRowKeys: dataCheckedRowKeys,
  onBatchDeleted: dataOnBatchDeleted,
  onDeleted: dataOnDeleted
} = useTableOperate(dataData, 'id', dataGetData);

watch(
  dataEditingData,
  v => {
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

function dataDefaultForm(): typeof dataDrawerForm {
  return {
    dictCode: '',
    label: '',
    value: '',
    css_class: '',
    list_class: '',
    is_default: false,
    status: '1',
    remark: ''
  };
}

async function onDataSubmit() {
  const valid = await dataDrawerFormRef.value?.validate().catch(() => false);
  if (!valid) {
    message.warning($t('common.pleaseCheckValue'));
    return;
  }
  const payload: Partial<DataRow> = { ...dataDrawerForm };
  const { error } =
    dataOperateType.value === 'add'
      ? await dictDataApi.add(payload)
      : await dictDataApi.update(dataEditingData.value!.id, payload);
  if (error) return;
  message.success(dataOperateType.value === 'add' ? $t('common.addSuccess') : $t('common.modifySuccess'));
  dataCloseDrawer();
  await dataGetData();
}

function createDataButtonEdit(row: DataRow) {
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

function createDataButtonDelete(row: DataRow) {
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
  dataGetDataByPage();
}
function onDataReset() {
  Object.assign(dataQueryForm, {
    keyword: '',
    status: ''
  });
  dataGetDataByPage();
}

watch(selectedDictTypeId, () => {
  if (selectedDictTypeId.value) {
    dataGetData();
  }
});

function handleDataAdd() {
  if (!selectedDictTypeId.value) {
    message.warning($t('page.system.dict.selectTypeFirst'));
    return;
  }
  dataHandleAdd();
}
</script>

<template>
  <div class="min-h-full">
    <NSpace vertical :size="12">
      <NTabs v-model:value="activeTab" type="line" animated>
        <NTabPane name="type" :tab="$t('page.system.dict.typeTab')">
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
                    :options="statusOptions"
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
                v-model:checked-row-keys="typeCheckedRowKeys"
                :columns="typeColumns"
                :data="typeData"
                :loading="typeLoading"
                :pagination="typeMobilePagination"
                :scroll-x="1500"
                :bordered="false"
                striped
              />
            </NCard>
          </NSpace>
        </NTabPane>

        <NTabPane name="data" :tab="$t('page.system.dict.dataTab')">
          <NSpace vertical :size="12">
            <NCard>
              <NForm inline label-placement="left" label-width="auto">
                <NFormItem :label="$t('page.system.dict.typeTab')" required>
                  <NSelect
                    v-model:value="selectedDictTypeId"
                    :options="dictTypeOptions.map(t => ({ label: t.name, value: t.id }))"
                    :placeholder="$t('page.system.dict.selectTypePlaceholder')"
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
                    :options="statusOptions"
                    clearable
                  />
                </NFormItem>
                <NFormItem>
                  <NSpace>
                    <NButton type="primary" :disabled="!selectedDictTypeId" @click="onDataSearch">
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
                v-model:checked-row-keys="dataCheckedRowKeys"
                :columns="dataColumns"
                :data="dataData"
                :loading="dataLoading"
                :pagination="dataMobilePagination"
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
              <NRadio value="1">{{ $t('page.system.common.enabled') }}</NRadio>
              <NRadio value="0">{{ $t('page.system.common.disabled') }}</NRadio>
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
          <NFormItem :label="$t('page.system.dict.form.code')" path="dictCode">
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
              <NRadio value="1">{{ $t('page.system.common.enabled') }}</NRadio>
              <NRadio value="0">{{ $t('page.system.common.disabled') }}</NRadio>
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
  </div>
</template>
