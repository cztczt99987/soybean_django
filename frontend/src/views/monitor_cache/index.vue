<script setup lang="tsx">
import { computed, reactive, ref } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import type { PaginationProps } from 'naive-ui';
import { cacheApi } from '@/service/api';
import { $t } from '@/locales';

defineOptions({ name: 'MonitorCache' });

type CacheRow = Api.Monitor.CacheRow;

/** 字节格式化 */
function formatBytes(n: number): string {
  if (!n || n <= 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(n) / Math.log(1024));
  return `${(n / 1024 ** i).toFixed(2)} ${units[i]}`;
}

/** TTL 秒格式化 */
function formatTtl(sec: number): string {
  if (sec < 0) return $t('page.monitor.cache.ttlNone');
  if (sec < 60) return `${sec}s`;
  if (sec < 3600) return `${Math.floor(sec / 60)}m ${sec % 60}s`;
  return `${Math.floor(sec / 3600)}h ${Math.floor((sec % 3600) / 60)}m`;
}

const loading = ref(false);
const mode = ref<'redis' | 'locmem'>('redis');
const records = ref<CacheRow[]>([]);
const keyword = ref('');
const checkedRowKeys = ref<Array<string | number>>([]);

const serverInfo = ref<Api.Monitor.CacheListResp['serverInfo']>({});

const pagination = reactive<PaginationProps>({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  prefix: info => $t('datatable.itemCount', { total: info.itemCount ?? 0 })
});

const isRedis = computed(() => mode.value === 'redis');

async function getData() {
  loading.value = true;

  try {
    const { data, error } = await cacheApi.list({ keyword: keyword.value || null });

    if (!error && data) {
      mode.value = data.mode;
      records.value = data.records ?? [];
      serverInfo.value = data.serverInfo ?? {};
      checkedRowKeys.value = [];
    }
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  getData();
}

function handleReset() {
  keyword.value = '';
  handleSearch();
}

async function handleDelete(key: string) {
  const { error } = await cacheApi.remove(key);

  if (!error) {
    window.$message?.success($t('page.monitor.cache.deleteSuccess'));
    getData();
  }
}

async function handleBatchDelete() {
  const keys = checkedRowKeys.value.map(String);
  if (!keys.length) return;

  const { error } = await cacheApi.batchRemove(keys);

  if (!error) {
    window.$message?.success($t('page.monitor.cache.deleteSuccess'));
    getData();
  }
}

async function handleCleanAll() {
  const { error } = await cacheApi.cleanAll();

  if (!error) {
    window.$message?.success($t('page.monitor.cache.deleteSuccess'));
    getData();
  }
}

const typeTagMap: Record<string, NaiveUI.ThemeColor> = {
  string: 'info',
  hash: 'success',
  list: 'warning',
  set: 'primary',
  zset: 'error'
};

const columns = computed<NaiveUI.TableColumn<CacheRow>[]>(() => [
  { type: 'selection', align: 'center', width: 48 },
  {
    key: 'index',
    title: $t('common.index'),
    align: 'center',
    width: 64,
    render: (_, index) => index + 1
  },
  {
    key: 'key',
    title: $t('page.monitor.cache.key'),
    align: 'center',
    minWidth: 240,
    ellipsis: { tooltip: true }
  },
  {
    key: 'type',
    title: $t('page.monitor.cache.type'),
    align: 'center',
    width: 100,
    render: row => <NTag type={typeTagMap[row.type] ?? 'default'}>{row.type}</NTag>
  },
  {
    key: 'size',
    title: $t('page.monitor.cache.size'),
    align: 'center',
    width: 120,
    render: row => formatBytes(row.size)
  },
  {
    key: 'ttl',
    title: $t('page.monitor.cache.ttl'),
    align: 'center',
    width: 140,
    render: row => <span>{formatTtl(row.ttl)}</span>
  },
  {
    key: 'operate',
    title: $t('common.operate'),
    align: 'center',
    width: 90,
    render: row => (
      <NPopconfirm onPositiveClick={() => handleDelete(row.key)}>
        {{
          default: () => $t('page.monitor.cache.deleteConfirm'),
          trigger: () => (
            <NButton type="error" ghost size="small">
              {$t('common.delete')}
            </NButton>
          )
        }}
      </NPopconfirm>
    )
  }
]);

getData();
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <template v-if="isRedis">
      <NCard :title="$t('page.monitor.cache.serverInfo')" :bordered="false" size="small" class="card-wrapper">
        <NGrid responsive="screen" :cols="5" :x-gap="16">
          <NGridItem :span="1">
            <NStatistic :label="$t('page.monitor.cache.redisVersion')" :value="serverInfo.redisVersion || '-'" />
          </NGridItem>
          <NGridItem :span="1">
            <NStatistic :label="$t('page.monitor.cache.usedMemory')" :value="serverInfo.usedMemoryHuman || '-'" />
          </NGridItem>
          <NGridItem :span="1">
            <NStatistic :label="$t('page.monitor.cache.maxMemory')" :value="serverInfo.maxMemoryHuman || '-'" />
          </NGridItem>
          <NGridItem :span="1">
            <NStatistic
              :label="$t('page.monitor.cache.connectedClients')"
              :value="String(serverInfo.connectedClients ?? '-')"
            />
          </NGridItem>
          <NGridItem :span="1">
            <NStatistic :label="$t('page.monitor.cache.dbSize')" :value="String(serverInfo.dbSize ?? '-')" />
          </NGridItem>
        </NGrid>
      </NCard>

      <NCard :bordered="false" size="small" class="card-wrapper">
        <NSpace wrap align="center">
          <NInput
            v-model:value="keyword"
            clearable
            class="w-240px"
            :placeholder="$t('page.monitor.cache.keywordPlaceholder')"
            @keyup.enter="handleSearch"
          />
          <NButton type="primary" ghost @click="handleSearch">
            <template #icon>
              <icon-ic-round-search class="text-icon" />
            </template>
            {{ $t('common.search') }}
          </NButton>
          <NButton @click="handleReset">
            <template #icon>
              <icon-ic-round-refresh class="text-icon" />
            </template>
            {{ $t('common.reset') }}
          </NButton>
        </NSpace>
      </NCard>

      <NCard :title="$t('page.monitor.cache.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
        <template #header-extra>
          <NSpace justify="end" wrap>
            <NPopconfirm @positive-click="handleBatchDelete">
              <template #trigger>
                <NButton size="small" ghost type="error" :disabled="checkedRowKeys.length === 0">
                  <template #icon>
                    <icon-ic-round-delete class="text-icon" />
                  </template>
                  {{ $t('common.batchDelete') }}
                </NButton>
              </template>
              {{ $t('page.monitor.cache.deleteConfirm') }}
            </NPopconfirm>
            <NPopconfirm @positive-click="handleCleanAll">
              <template #trigger>
                <NButton size="small" ghost type="warning">
                  {{ $t('page.monitor.cache.cleanAll') }}
                </NButton>
              </template>
              {{ $t('page.monitor.cache.cleanAllConfirm') }}
            </NPopconfirm>
            <NButton size="small" @click="getData">
              <template #icon>
                <icon-mdi-refresh class="text-icon" :class="{ 'animate-spin': loading }" />
              </template>
              {{ $t('common.refresh') }}
            </NButton>
          </NSpace>
        </template>
        <NDataTable
          v-model:checked-row-keys="checkedRowKeys"
          v-model:page="pagination.page"
          :columns="columns"
          :data="records"
          size="small"
          :flex-height="true"
          :loading="loading"
          :row-key="(row: CacheRow) => row.key"
          :pagination="pagination"
          class="sm:h-full"
        />
      </NCard>
    </template>

    <NCard v-else :title="$t('page.monitor.cache.title')" :bordered="false" size="small" class="card-wrapper">
      <NEmpty :description="$t('page.monitor.cache.notRedis')" class="py-48px" />
    </NCard>
  </div>
</template>

<style scoped></style>
