<script setup lang="tsx">
import { ref } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import type { ConfigValueType, EnableStatus } from '@/constants/business';
import { enableStatusRecord, valueTypeRecord } from '@/constants/business';
import { configApi } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { $t } from '@/locales';
import ConfigOperateDrawer from './modules/config-operate-drawer.vue';
import ConfigSearch from './modules/config-search.vue';

const appStore = useAppStore();

const searchParams = ref<Api.System.ConfigSearchParams>({
  current: 1,
  size: 10,
  keyword: null,
  name: null,
  code: null,
  status: null
});

const { columns, columnChecks, data, getData, getDataByPage, loading, mobilePagination } = useNaivePaginatedTable({
  api: () => configApi.list(searchParams.value),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    searchParams.value.current = params.page;
    searchParams.value.size = params.pageSize;
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
      title: $t('page.system.config.form.name'),
      align: 'center',
      width: 160
    },
    {
      key: 'code',
      title: $t('page.system.config.form.code'),
      align: 'center',
      width: 180
    },
    {
      key: 'value',
      title: $t('page.system.config.form.value'),
      align: 'center',
      width: 200
    },
    {
      key: 'value_type',
      title: $t('page.system.config.form.valueType'),
      align: 'center',
      width: 100,
      render: row => {
        if (!row.value_type) {
          return null;
        }

        const tagMap: Record<ConfigValueType, NaiveUI.ThemeColor> = {
          S: 'primary',
          N: 'info',
          B: 'warning',
          J: 'success'
        };

        return <NTag type={tagMap[row.value_type]}>{$t(valueTypeRecord[row.value_type])}</NTag>;
      }
    },
    {
      key: 'is_system',
      title: $t('page.system.config.form.isSystem'),
      align: 'center',
      width: 100,
      render: row => (
        <NTag type={row.is_system ? 'success' : 'default'}>
          {$t(row.is_system ? 'common.yesOrNo.yes' : 'common.yesOrNo.no')}
        </NTag>
      )
    },
    {
      key: 'status',
      title: $t('page.system.config.form.status'),
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
      width: 180,
      fixed: 'right',
      render: row => (
        <div class="flex-center gap-8px">
          <NButton type="primary" ghost size="small" onClick={() => edit(row.id)}>
            {$t('common.edit')}
          </NButton>
          <NPopconfirm onPositiveClick={() => handleDelete(row.id)}>
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

const { drawerVisible, operateType, editingData, handleAdd, handleEdit, checkedRowKeys, onBatchDeleted, onDeleted } =
  useTableOperate(data, 'id', getData);

async function handleBatchDelete() {
  await configApi.batchDelete(checkedRowKeys.value.map(Number));

  onBatchDeleted();
}

async function handleDelete(id: number) {
  await configApi.remove(id);

  onDeleted();
}

function edit(id: number) {
  handleEdit(id);
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <ConfigSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard
      :title="$t('page.system.config.title')"
      :bordered="false"
      size="small"
      class="card-wrapper sm:flex-1-hidden"
    >
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          @add="handleAdd"
          @delete="handleBatchDelete"
          @refresh="getData"
        />
      </template>
      <NDataTable
        v-model:checked-row-keys="checkedRowKeys"
        :columns="columns"
        :data="data"
        size="small"
        :flex-height="!appStore.isMobile"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        :scroll-x="1312"
        class="sm:h-full"
      />
      <ConfigOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getDataByPage"
      />
    </NCard>
  </div>
</template>
