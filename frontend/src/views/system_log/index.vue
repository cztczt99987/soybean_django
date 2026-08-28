<script setup lang="tsx">
import { computed, ref } from 'vue';
import { NButton, NPopconfirm, NTag, NInputNumber } from 'naive-ui';
import type { OperationType } from '@/constants/business';
import { operationTypeRecord } from '@/constants/business';
import { logApi } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { $t } from '@/locales';
import LogSearch from './modules/log-search.vue';

defineOptions({ name: 'SystemLog' });

const appStore = useAppStore();

const searchParams = ref<Api.System.LogSearchParams>({
  current: 1,
  size: 10,
  keyword: null,
  username: null,
  module: null,
  description: null,
  operationType: null,
  status: null,
  beginTime: null,
  endTime: null
});

/** 操作类型 → 标签色映射（与后端 TYPE_CHOICES 语义对应） */
const operationTypeTagMap: Record<OperationType, NaiveUI.ThemeColor> = {
  '1': 'default',
  '2': 'success',
  '3': 'warning',
  '4': 'error',
  '5': 'primary',
  '6': 'info',
  '7': 'info',
  '8': 'success',
  '9': 'error'
};

const { columns, columnChecks, data, getData, getDataByPage, loading, mobilePagination } = useNaivePaginatedTable({
  api: () => logApi.list(searchParams.value),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    searchParams.value.current = params.page;
    searchParams.value.size = params.pageSize;
  },
  columns: () => [
    {
      type: 'selection',
      align: 'center',
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
      key: 'username',
      title: $t('page.system.log.fields.username'),
      align: 'center',
      width: 120
    },
    {
      key: 'module',
      title: $t('page.system.log.fields.module'),
      align: 'center',
      width: 120
    },
    {
      key: 'description',
      title: $t('page.system.log.fields.description'),
      align: 'center',
      width: 200,
      ellipsis: { tooltip: true }
    },
    {
      key: 'operation_type',
      title: $t('page.system.log.fields.operationType'),
      align: 'center',
      width: 100,
      render: row => {
        if (!row.operation_type) {
          return null;
        }

        return <NTag type={operationTypeTagMap[row.operation_type]}>{$t(operationTypeRecord[row.operation_type])}</NTag>;
      }
    },
    {
      key: 'method',
      title: $t('page.system.log.fields.method'),
      align: 'center',
      width: 90
    },
    {
      key: 'request_url',
      title: $t('page.system.log.fields.url'),
      align: 'center',
      width: 260,
      ellipsis: { tooltip: true }
    },
    {
      key: 'ip',
      title: $t('page.system.log.fields.ip'),
      align: 'center',
      width: 140
    },
    {
      key: 'status',
      title: $t('page.system.log.fields.status'),
      align: 'center',
      width: 90,
      render: row => {
        if (!row.status) {
          return null;
        }

        const tagMap: Record<'1' | '0', NaiveUI.ThemeColor> = {
          '1': 'success',
          '0': 'error'
        };
        const label = row.status === '1' ? $t('page.system.common.success') : $t('page.system.common.failure');

        return <NTag type={tagMap[row.status]}>{label}</NTag>;
      }
    },
    {
      key: 'cost_time',
      title: $t('page.system.log.fields.costTime'),
      align: 'center',
      width: 100,
      render: row => `${row.cost_time} ms`
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
      width: 90,
      fixed: 'right',
      render: row => (
        <div class="flex-center gap-8px">
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

const { checkedRowKeys, onBatchDeleted, onDeleted } = useTableOperate(data, 'id', getData);

async function handleBatchDelete() {
  await logApi.batchDelete(checkedRowKeys.value.map(Number));

  onBatchDeleted();
}

async function handleDelete(id: number) {
  await logApi.remove(id);

  onDeleted();
}

/** 清理 N 天前日志 */
const cleanVisible = ref(false);
const cleanDays = ref<number>(30);
const cleanLoading = ref(false);

const cleanTitle = computed(() => $t('page.system.log.action.clean'));

function handleOpenClean() {
  cleanDays.value = 30;
  cleanVisible.value = true;
}

async function handleClean() {
  cleanLoading.value = true;

  try {
    const { error } = await logApi.clean(cleanDays.value);

    if (!error) {
      window.$message?.success($t('page.system.common.cleanSuccess'));

      cleanVisible.value = false;

      await getDataByPage();
    }
  } finally {
    cleanLoading.value = false;
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <LogSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard :title="$t('page.system.log.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <TableHeaderOperation v-model:columns="columnChecks" :loading="loading" @refresh="getData">
          <template #prefix>
            <NButton size="small" ghost type="warning" @click="handleOpenClean">
              <template #icon>
                <icon-ic-round-delete class="text-icon" />
              </template>
              {{ cleanTitle }}
            </NButton>
          </template>
          <template #default>
            <NPopconfirm @positive-click="handleBatchDelete">
              <template #trigger>
                <NButton size="small" ghost type="error" :disabled="checkedRowKeys.length === 0">
                  <template #icon>
                    <icon-ic-round-delete class="text-icon" />
                  </template>
                  {{ $t('common.batchDelete') }}
                </NButton>
              </template>
              {{ $t('common.confirmDelete') }}
            </NPopconfirm>
          </template>
        </TableHeaderOperation>
      </template>
      <NDataTable
        v-model:checked-row-keys="checkedRowKeys"
        :columns="columns"
        :data="data"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="1620"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        class="sm:h-full"
      />
    </NCard>
    <NModal v-model:show="cleanVisible" preset="card" :title="cleanTitle" class="w-420px">
      <div class="flex items-center gap-12px">
        <span>{{ $t('page.system.log.action.cleanDays') }}</span>
        <NInputNumber v-model:value="cleanDays" :min="0" :max="3650" class="flex-1" />
        <span>{{ $t('page.system.log.action.day') }}</span>
      </div>
      <template #footer>
        <NSpace justify="end" :size="16">
          <NButton @click="cleanVisible = false">{{ $t('common.cancel') }}</NButton>
          <NButton type="primary" :loading="cleanLoading" @click="handleClean">{{ $t('common.confirm') }}</NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>

<style scoped></style>
