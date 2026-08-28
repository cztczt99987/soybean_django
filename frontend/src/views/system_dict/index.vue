<script setup lang="tsx">
import { computed, ref, watch } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import type { EnableStatus } from '@/constants/business';
import { enableStatusRecord } from '@/constants/business';
import { dictDataApi, dictTypeApi } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { $t } from '@/locales';
import DictDataOperateDrawer from './modules/dict-data-operate-drawer.vue';
import DictDataSearch from './modules/dict-data-search.vue';
import DictTypeOperateDrawer from './modules/dict-type-operate-drawer.vue';
import DictTypeSearch from './modules/dict-type-search.vue';

const appStore = useAppStore();

/* ---------- 字典类型 Tab ---------- */

const typeSearchParams = ref<Api.System.DictTypeSearchParams>({
  current: 1,
  size: 10,
  keyword: null,
  name: null,
  code: null,
  status: null
});

const {
  columns: typeColumns,
  columnChecks: typeColumnChecks,
  data: typeData,
  getData: typeGetData,
  getDataByPage: typeGetDataByPage,
  loading: typeLoading,
  mobilePagination: typeMobilePagination
} = useNaivePaginatedTable({
  api: () => dictTypeApi.list(typeSearchParams.value),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    typeSearchParams.value.current = params.page;
    typeSearchParams.value.size = params.pageSize;
  },
  columns: () => [
    {
      type: 'selection',
      width: 48
    },
    {
      key: 'index',
      title: $t('common.index'),
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'name',
      title: $t('page.system.dict.form.name'),
      align: 'center',
      width: 160
    },
    {
      key: 'code',
      title: $t('page.system.dict.form.code'),
      align: 'center',
      width: 160
    },
    {
      key: 'status',
      title: $t('page.system.dict.form.status'),
      align: 'center',
      width: 100,
      render: row => {
        if (!row.status) {
          return null;
        }

        const tagMap: Record<EnableStatus, NaiveUI.ThemeColor> = {
          '1': 'success',
          '0': 'warning'
        };

        return <NTag type={tagMap[row.status]}>{$t(enableStatusRecord[row.status])}</NTag>;
      }
    },
    {
      key: 'remark',
      title: $t('page.system.dict.form.remark'),
      align: 'center',
      width: 150
    },
    {
      key: 'created_at',
      title: $t('page.system.common.createdAt'),
      align: 'center',
      width: 150
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 128,
      fixed: 'right',
      render: row => (
        <div class="flex-center gap-8px">
          <NButton type="primary" ghost size="small" onClick={() => typeHandleEdit(row.id)}>
            {$t('common.edit')}
          </NButton>
          <NPopconfirm onPositiveClick={() => handleTypeDelete(row.id)}>
            {{
              default: () => $t('common.confirmDelete'),
              trigger: () => (
                <NButton type="error" ghost size="small">
                  {$t('common.delete')}
                </NButton>
              )
            }}
          </NPopconfirm>
        </div>
      )
    }
  ]
});

const {
  drawerVisible: typeDrawerVisible,
  operateType: typeOperateType,
  editingData: typeEditingData,
  handleAdd: typeHandleAdd,
  handleEdit: typeHandleEdit,
  checkedRowKeys: typeCheckedRowKeys,
  onBatchDeleted: typeOnBatchDeleted,
  onDeleted: typeOnDeleted
} = useTableOperate(typeData, 'id', typeGetData);

async function handleTypeBatchDelete() {
  await dictTypeApi.batchDelete(typeCheckedRowKeys.value.map(Number));

  typeOnBatchDeleted();

  await getTypeOptions();
}

function typeEdit(id: number) {
  typeHandleEdit(id);
}

async function handleTypeDelete(id: number) {
  await dictTypeApi.remove(id);

  typeOnDeleted();

  await getTypeOptions();
}

async function handleTypeSubmitted() {
  await typeGetDataByPage();

  await getTypeOptions();
}

/* ---------- 字典数据 Tab ---------- */

const typeOptions = ref<{ id: number; name: string; code: string }[]>([]);

async function getTypeOptions() {
  const { data, error } = await dictTypeApi.options();

  if (!error) {
    typeOptions.value = data ?? [];
  }
}

getTypeOptions();

const typeSelectOptions = computed(() => typeOptions.value.map(item => ({ label: item.name, value: item.id })));

const selectedTypeId = ref<number | null>(null);

const selectedCode = computed(() => typeOptions.value.find(item => item.id === selectedTypeId.value)?.code ?? null);

const dataSearchParams = ref<Api.System.DictDataSearchParams>({
  current: 1,
  size: 10,
  keyword: null,
  label: null,
  status: null
});

const {
  columns: dataColumns,
  columnChecks: dataColumnChecks,
  data: dataData,
  getData: dataGetData,
  getDataByPage: dataGetDataByPage,
  loading: dataLoading,
  mobilePagination: dataMobilePagination
} = useNaivePaginatedTable({
  immediate: false,
  api: () => dictDataApi.list({ ...dataSearchParams.value, dictCode: selectedCode.value || undefined }),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    dataSearchParams.value.current = params.page;
    dataSearchParams.value.size = params.pageSize;
  },
  columns: () => [
    {
      type: 'selection',
      width: 48
    },
    {
      key: 'index',
      title: $t('common.index'),
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'label',
      title: $t('page.system.dict.data.label'),
      align: 'center',
      width: 190
    },
    {
      key: 'value',
      title: $t('page.system.dict.data.value'),
      align: 'center',
      width: 190
    },
    {
      key: 'css_class',
      title: $t('page.system.dict.data.cssClass'),
      align: 'center',
      width: 150
    },
    {
      key: 'list_class',
      title: $t('page.system.dict.data.listClass'),
      align: 'center',
      width: 150
    },
    {
      key: 'is_default',
      title: $t('page.system.dict.data.isDefault'),
      align: 'center',
      width: 100,
      render: row => (
        <NTag type={row.is_default ? 'success' : 'default'}>
          {row.is_default ? $t('common.yesOrNo.yes') : $t('common.yesOrNo.no')}
        </NTag>
      )
    },
    {
      key: 'status',
      title: $t('page.system.dict.data.status'),
      align: 'center',
      width: 100,
      render: row => {
        if (!row.status) {
          return null;
        }

        const tagMap: Record<EnableStatus, NaiveUI.ThemeColor> = {
          '1': 'success',
          '0': 'warning'
        };

        return <NTag type={tagMap[row.status]}>{$t(enableStatusRecord[row.status])}</NTag>;
      }
    },
    {
      key: 'created_at',
      title: $t('page.system.common.createdAt'),
      align: 'center',
      width: 180
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 128,
      fixed: 'right',
      render: row => (
        <div class="flex-center gap-8px">
          <NButton type="primary" ghost size="small" onClick={() => dataHandleEdit(row.id)}>
            {$t('common.edit')}
          </NButton>
          <NPopconfirm onPositiveClick={() => handleDataDelete(row.id)}>
            {{
              default: () => $t('common.confirmDelete'),
              trigger: () => (
                <NButton type="error" ghost size="small">
                  {$t('common.delete')}
                </NButton>
              )
            }}
          </NPopconfirm>
        </div>
      )
    }
  ]
});

const {
  drawerVisible: dataDrawerVisible,
  operateType: dataOperateType,
  editingData: dataEditingData,
  handleAdd: dataHandleAdd,
  handleEdit: dataHandleEdit,
  checkedRowKeys: dataCheckedRowKeys,
  onBatchDeleted: dataOnBatchDeleted,
  onDeleted: dataOnDeleted
} = useTableOperate(dataData, 'id', dataGetData);

async function handleDataBatchDelete() {
  await dictDataApi.batchDelete(dataCheckedRowKeys.value.map(Number));

  dataOnBatchDeleted();
}

function dataEdit(id: number) {
  dataHandleEdit(id);
}

async function handleDataDelete(id: number) {
  await dictDataApi.remove(id);

  dataOnDeleted();
}

function handleDataAdd() {
  if (!selectedTypeId.value) {
    window.$message?.warning($t('page.system.dict.selectTypeFirst'));

    return;
  }

  dataHandleAdd();
}

watch(selectedTypeId, val => {
  dataSearchParams.value.current = 1;
  dataCheckedRowKeys.value = [];

  if (val === null) {
    return;
  }

  dataGetDataByPage();
});
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NCard :title="$t('page.system.dict.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <NTabs type="line" animated>
        <NTabPane name="type" :tab="$t('page.system.dict.typeTab')">
          <div class="flex-col-stretch gap-16px">
            <DictTypeSearch v-model:model="typeSearchParams" @search="typeGetDataByPage" />
            <TableHeaderOperation
              v-model:columns="typeColumnChecks"
              :disabled-delete="typeCheckedRowKeys.length === 0"
              :loading="typeLoading"
              @add="typeHandleAdd"
              @delete="handleTypeBatchDelete"
              @refresh="typeGetData"
            />
            <NDataTable
              v-model:checked-row-keys="typeCheckedRowKeys"
              :columns="typeColumns"
              :data="typeData"
              size="small"
              :flex-height="!appStore.isMobile"
              :scroll-x="960"
              :loading="typeLoading"
              remote
              :row-key="row => row.id"
              :pagination="typeMobilePagination"
              class="sm:h-full"
              striped
            />
            <DictTypeOperateDrawer
              v-model:visible="typeDrawerVisible"
              :operate-type="typeOperateType"
              :row-data="typeEditingData"
              @submitted="handleTypeSubmitted"
            />
          </div>
        </NTabPane>
        <NTabPane name="data" :tab="$t('page.system.dict.dataTab')">
          <div class="flex-col-stretch gap-16px">
            <NSelect
              v-model:value="selectedTypeId"
              :options="typeSelectOptions"
              :placeholder="$t('page.system.dict.selectTypePlaceholder')"
              clearable
              filterable
              class="w-320px"
            />
            <NAlert v-if="!selectedTypeId" type="info" :title="$t('page.system.dict.selectTypeFirst')" />
            <DictDataSearch v-model:model="dataSearchParams" @search="dataGetDataByPage" />
            <TableHeaderOperation
              v-model:columns="dataColumnChecks"
              :disabled-delete="dataCheckedRowKeys.length === 0"
              :loading="dataLoading"
              @add="handleDataAdd"
              @delete="handleDataBatchDelete"
              @refresh="dataGetData"
            />
            <NDataTable
              v-model:checked-row-keys="dataCheckedRowKeys"
              :columns="dataColumns"
              :data="selectedTypeId ? dataData : []"
              size="small"
              :flex-height="!appStore.isMobile"
              :scroll-x="1300"
              :loading="dataLoading"
              remote
              :row-key="row => row.id"
              :pagination="dataMobilePagination"
              class="sm:h-full"
              striped
            />
            <DictDataOperateDrawer
              v-model:visible="dataDrawerVisible"
              :operate-type="dataOperateType"
              :row-data="dataEditingData"
              :dict-type-id="selectedTypeId"
              @submitted="dataGetDataByPage"
            />
          </div>
        </NTabPane>
      </NTabs>
    </NCard>
  </div>
</template>
