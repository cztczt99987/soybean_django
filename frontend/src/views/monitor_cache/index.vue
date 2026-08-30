<script setup lang="tsx">
import { computed, nextTick, ref, watch } from 'vue';
import { NButton, NPopconfirm } from 'naive-ui';
import type { ECOption } from '@/hooks/common/echarts';
import { useEcharts } from '@/hooks/common/echarts';
import { cacheApi } from '@/service/api';
import { $t } from '@/locales';

defineOptions({ name: 'MonitorCache' });

type CacheRow = Api.Monitor.CacheRow;
type CategoryRow = Api.Monitor.CacheCategorySummary;
type ServerInfo = Api.Monitor.CacheListResp['serverInfo'];

const loading = ref(false);
const mode = ref<'redis' | 'locmem'>('redis');
const records = ref<CacheRow[]>([]);
const categories = ref<CategoryRow[]>([]);
const serverInfo = ref<ServerInfo>({});

/** 当前标签页：监控信息 / 缓存管理 */
const activeTab = ref<'monitor' | 'manage'>('monitor');

/** 当前选中的分类与键名 */
const selectedCategory = ref<string | null>(null);
const selectedKey = ref<string | null>(null);
const detail = ref<Api.Monitor.CacheDetailResp | null>(null);

const isRedis = computed(() => mode.value === 'redis');

/** 左栏：分类列表 */
const categoryRows = computed(() => categories.value);

/** 中栏：选中分类下的键名列表 */
const keyRows = computed(() =>
  selectedCategory.value ? records.value.filter(row => row.category === selectedCategory.value) : []
);

/** 命令统计饼图配置（玫瑰图，取调用量前 12 的命令） */
function buildPieOption(): ECOption {
  const stats = serverInfo.value.commandStats ?? {};
  const data = Object.entries(stats)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 12);

  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} 次 ({d}%)' },
    legend: { type: 'scroll', orient: 'vertical', right: 0, top: 'middle', textStyle: { fontSize: 11 } },
    series: [
      {
        type: 'pie',
        radius: ['25%', '80%'],
        center: ['38%', '50%'],
        roseType: 'radius',
        itemStyle: { borderRadius: 4 },
        label: { show: false },
        data
      }
    ]
  };
}

/** 内存信息仪表盘配置 */
function buildGaugeOption(): ECOption {
  const used = serverInfo.value.usedMemory ?? 0;
  const maxMemory = serverInfo.value.maxMemory ?? 0;
  // 未配置 maxmemory 时，按当前用量的 1.25 倍（至少 1M）撑起刻度
  const axisMax = maxMemory > 0 ? maxMemory : Math.max(Math.ceil(used * 1.25), 1024 * 1024);

  return {
    series: [
      {
        type: 'gauge',
        min: 0,
        max: axisMax,
        startAngle: 210,
        endAngle: -30,
        axisLine: { lineStyle: { width: 14 } },
        axisTick: { distance: -18 },
        splitLine: { distance: -22, length: 12 },
        axisLabel: { distance: -32, fontSize: 10, formatter: fmtAxisBytes },
        pointer: { itemStyle: { color: 'auto' } },
        detail: {
          formatter: () => serverInfo.value.usedMemoryHuman || '0B',
          fontSize: 20,
          offsetCenter: [0, '55%']
        },
        title: { offsetCenter: [0, '85%'], fontSize: 12 },
        data: [{ value: used, name: $t('page.monitor.cache.memoryUsage') }]
      }
    ]
  };
}

/** 仪表盘刻度字节缩写 */
function fmtAxisBytes(v: number): string {
  if (v >= 1024 ** 3) return `${(v / 1024 ** 3).toFixed(0)}G`;
  if (v >= 1024 ** 2) return `${(v / 1024 ** 2).toFixed(0)}M`;
  if (v >= 1024) return `${(v / 1024).toFixed(0)}K`;
  return `${v}B`;
}

const { domRef: pieDomRef, updateOptions: updatePieOption } = useEcharts<ECOption>(buildPieOption);
const { domRef: gaugeDomRef, updateOptions: updateGaugeOption } = useEcharts<ECOption>(buildGaugeOption);

async function updateCharts() {
  await Promise.all([updatePieOption(buildPieOption), updateGaugeOption(buildGaugeOption)]);
}

// 切回监控信息标签时容器重新可见，需要重新渲染/刷新图表（隐藏期间容器尺寸为 0）
watch(activeTab, async tab => {
  if (tab === 'monitor') {
    await nextTick();
    await updateCharts();
  }
});

async function getData() {
  loading.value = true;

  try {
    const { data, error } = await cacheApi.list();

    if (!error && data) {
      mode.value = data.mode;
      records.value = data.records ?? [];
      categories.value = data.categories ?? [];
      serverInfo.value = data.serverInfo ?? {};

      // 刷新后若选中的分类/键已不存在则清空
      if (selectedCategory.value && !categories.value.some(item => item.name === selectedCategory.value)) {
        selectedCategory.value = null;
        selectedKey.value = null;
        detail.value = null;
      }

      await updateCharts();
    }
  } finally {
    loading.value = false;
  }
}

/** 选择分类，展示该分类下的键名 */
function handleSelectCategory(row: CategoryRow) {
  selectedCategory.value = row.name;
  selectedKey.value = null;
  detail.value = null;
}

/** 查看键内容 */
async function handleViewKey(row: CacheRow) {
  selectedKey.value = row.key;
  const { data, error } = await cacheApi.detail(row.key);

  if (!error && data) {
    detail.value = data;
  }
}

async function handleDelete(key: string) {
  const { error } = await cacheApi.remove(key);

  if (!error) {
    window.$message?.success($t('page.monitor.cache.deleteSuccess'));
    if (selectedKey.value === key) {
      selectedKey.value = null;
      detail.value = null;
    }
    getData();
  }
}

async function handleDeleteCategory(category: string) {
  const { error } = await cacheApi.removeCategory(category);

  if (!error) {
    window.$message?.success($t('page.monitor.cache.deleteSuccess'));
    if (selectedCategory.value === category) {
      selectedCategory.value = null;
      selectedKey.value = null;
      detail.value = null;
    }
    getData();
  }
}

async function handleCleanAll() {
  const { error } = await cacheApi.cleanAll();

  if (!error) {
    window.$message?.success($t('page.monitor.cache.deleteSuccess'));
    selectedCategory.value = null;
    selectedKey.value = null;
    detail.value = null;
    getData();
  }
}

/** 左栏表格列：缓存名称（点击选中）/ 备注 / 操作 */
const categoryColumns = computed<NaiveUI.TableColumn<CategoryRow>[]>(() => [
  {
    key: 'name',
    title: $t('page.monitor.cache.cacheName'),
    align: 'left',
    minWidth: 120,
    ellipsis: { tooltip: true },
    render: row => (
      <NButton text type="primary" size="small" onClick={() => handleSelectCategory(row)}>
        {row.name}
      </NButton>
    )
  },
  {
    key: 'label',
    title: $t('page.monitor.cache.remark'),
    align: 'left',
    minWidth: 100,
    ellipsis: { tooltip: true },
    render: row => <span class="text-gray-500">{row.label}</span>
  },
  {
    key: 'operate',
    title: $t('common.operate'),
    align: 'center',
    width: 60,
    render: row => (
      <NPopconfirm onPositiveClick={() => handleDeleteCategory(row.name)}>
        {{
          default: () => $t('page.monitor.cache.deleteCategoryConfirm'),
          trigger: () => (
            <NButton type="error" text size="small">
              <icon-ic-round-delete class="text-icon" />
            </NButton>
          )
        }}
      </NPopconfirm>
    )
  }
]);

/** 中栏表格列：缓存键名（点击查看内容）/ 操作 */
const keyColumns = computed<NaiveUI.TableColumn<CacheRow>[]>(() => [
  {
    key: 'key',
    title: $t('page.monitor.cache.cacheKeyName'),
    align: 'left',
    minWidth: 160,
    ellipsis: { tooltip: true },
    render: row => (
      <NButton text type="primary" size="small" onClick={() => handleViewKey(row)}>
        {row.key}
      </NButton>
    )
  },
  {
    key: 'operate',
    title: $t('common.operate'),
    align: 'center',
    width: 60,
    render: row => (
      <NPopconfirm onPositiveClick={() => handleDelete(row.key)}>
        {{
          default: () => $t('page.monitor.cache.deleteConfirm'),
          trigger: () => (
            <NButton type="error" text size="small">
              <icon-ic-round-delete class="text-icon" />
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
      <NTabs v-model:value="activeTab" type="line" class="flex-1-hidden">
        <!-- 标签页 1：监控信息 -->
        <NTabPane name="monitor" :tab="$t('page.monitor.cache.monitorInfoTab')" display-directive="show">
          <div class="flex-col-stretch gap-16px overflow-auto">
            <NCard :title="$t('page.monitor.cache.redisInfo')" :bordered="false" size="small" class="card-wrapper">
              <template #header-extra>
                <NButton size="small" quaternary circle @click="getData">
                  <icon-mdi-refresh class="text-icon" :class="{ 'animate-spin': loading }" />
                </NButton>
              </template>
              <NDescriptions bordered size="small" :column="6" label-placement="left">
                <NDescriptionsItem :label="$t('page.monitor.cache.redisVersion')">
                  {{ serverInfo.redisVersion || '-' }}
                </NDescriptionsItem>
                <NDescriptionsItem :label="$t('page.monitor.cache.runMode')">
                  {{ serverInfo.runMode || '-' }}
                </NDescriptionsItem>
                <NDescriptionsItem :label="$t('page.monitor.cache.port')">
                  {{ serverInfo.port ?? '-' }}
                </NDescriptionsItem>
                <NDescriptionsItem :label="$t('page.monitor.cache.connectedClients')">
                  {{ serverInfo.connectedClients ?? '-' }}
                </NDescriptionsItem>
                <NDescriptionsItem :label="$t('page.monitor.cache.uptimeDays')">
                  {{ serverInfo.uptimeDays ?? '-' }}
                </NDescriptionsItem>
                <NDescriptionsItem :label="$t('page.monitor.cache.usedMemory')">
                  {{ serverInfo.usedMemoryHuman || '-' }}
                </NDescriptionsItem>
                <NDescriptionsItem :label="$t('page.monitor.cache.usedCpu')">
                  {{ serverInfo.usedCpuPercent ?? '-' }}
                </NDescriptionsItem>
                <NDescriptionsItem :label="$t('page.monitor.cache.memoryConfig')">
                  {{ serverInfo.maxMemoryHuman || '-' }}
                </NDescriptionsItem>
                <NDescriptionsItem label="AOF">
                  {{ serverInfo.aofEnabled ? $t('page.monitor.cache.aofOn') : $t('page.monitor.cache.aofOff') }}
                </NDescriptionsItem>
                <NDescriptionsItem :label="$t('page.monitor.cache.rdbStatus')">
                  {{ serverInfo.rdbStatus || '-' }}
                </NDescriptionsItem>
                <NDescriptionsItem :label="$t('page.monitor.cache.dbSize')">
                  {{ serverInfo.dbSize ?? '-' }}
                </NDescriptionsItem>
                <NDescriptionsItem :label="$t('page.monitor.cache.netIo')">
                  {{ serverInfo.netInKps ?? 0 }}kps / {{ serverInfo.netOutKps ?? 0 }}kps
                </NDescriptionsItem>
              </NDescriptions>
            </NCard>

            <div class="flex gap-16px lt-sm:flex-col">
              <NCard
                :title="$t('page.monitor.cache.commandStats')"
                :bordered="false"
                size="small"
                class="card-wrapper flex-1"
              >
                <div ref="pieDomRef" class="h-360px w-full" />
              </NCard>
              <NCard
                :title="$t('page.monitor.cache.memoryInfo')"
                :bordered="false"
                size="small"
                class="card-wrapper w-460px shrink-0 lt-sm:w-full"
              >
                <div ref="gaugeDomRef" class="h-360px w-full" />
              </NCard>
            </div>
          </div>
        </NTabPane>

        <!-- 标签页 2：缓存管理（三栏） -->
        <NTabPane name="manage" :tab="$t('page.monitor.cache.cacheManageTab')" display-directive="show">
          <div class="flex flex-1 min-h-640px gap-16px lt-sm:flex-col">
            <!-- 左栏：缓存列表（分类） -->
            <NCard
              :title="$t('page.monitor.cache.cacheList')"
              :bordered="false"
              size="small"
              class="card-wrapper w-340px shrink-0 lt-sm:w-full"
            >
              <template #header-extra>
                <NButton size="small" quaternary circle @click="getData">
                  <icon-mdi-refresh class="text-icon" :class="{ 'animate-spin': loading }" />
                </NButton>
              </template>
              <NDataTable
                :columns="categoryColumns"
                :data="categoryRows"
                size="small"
                :loading="loading"
                :row-key="(row: CategoryRow) => row.name"
                :flex-height="true"
                class="h-full"
                :row-class-name="(row: CategoryRow) => (row.name === selectedCategory ? 'row-selected' : '')"
                :row-props="
                  (row: CategoryRow) => ({
                    style: 'cursor: pointer;',
                    onClick: () => handleSelectCategory(row)
                  })
                "
              />
            </NCard>

            <!-- 中栏：键名列表 -->
            <NCard
              :title="$t('page.monitor.cache.keyList')"
              :bordered="false"
              size="small"
              class="card-wrapper min-w-0 flex-1"
            >
              <template #header-extra>
                <NButton size="small" quaternary circle @click="getData">
                  <icon-mdi-refresh class="text-icon" :class="{ 'animate-spin': loading }" />
                </NButton>
              </template>
              <NDataTable
                v-if="selectedCategory"
                :columns="keyColumns"
                :data="keyRows"
                size="small"
                :loading="loading"
                :row-key="(row: CacheRow) => row.key"
                :flex-height="true"
                class="h-full"
                :row-class-name="(row: CacheRow) => (row.key === selectedKey ? 'row-selected' : '')"
                :row-props="
                  (row: CacheRow) => ({
                    style: 'cursor: pointer;',
                    onClick: () => handleViewKey(row)
                  })
                "
              />
              <NEmpty v-else :description="$t('page.monitor.cache.selectCategoryTip')" class="py-48px" />
            </NCard>

            <!-- 右栏：缓存内容 -->
            <NCard
              :title="$t('page.monitor.cache.cacheContent')"
              :bordered="false"
              size="small"
              class="card-wrapper w-400px shrink-0 lt-sm:w-full"
            >
              <template #header-extra>
                <NPopconfirm @positive-click="handleCleanAll">
                  <template #trigger>
                    <NButton size="small" text type="error">
                      <template #icon>
                        <icon-ic-round-delete class="text-icon" />
                      </template>
                      {{ $t('page.monitor.cache.cleanAll') }}
                    </NButton>
                  </template>
                  {{ $t('page.monitor.cache.cleanAllConfirm') }}
                </NPopconfirm>
              </template>
              <template v-if="detail">
                <NForm label-placement="top" size="small">
                  <NFormItem :label="$t('page.monitor.cache.cacheName')">
                    <NInput :value="detail.type" readonly />
                  </NFormItem>
                  <NFormItem :label="$t('page.monitor.cache.cacheKeyName')">
                    <NInput :value="detail.key" readonly />
                  </NFormItem>
                  <NFormItem :label="$t('page.monitor.cache.cacheContent')">
                    <NInput
                      :value="detail.value"
                      type="textarea"
                      readonly
                      placeholder=""
                      :autosize="{ minRows: 10, maxRows: 22 }"
                    />
                  </NFormItem>
                </NForm>
              </template>
              <NEmpty v-else :description="$t('page.monitor.cache.selectKeyTip')" class="py-48px" />
            </NCard>
          </div>
        </NTabPane>
      </NTabs>
    </template>

    <NCard v-else :title="$t('page.monitor.cache.title')" :bordered="false" size="small" class="card-wrapper">
      <NEmpty :description="$t('page.monitor.cache.notRedis')" class="py-48px" />
    </NCard>
  </div>
</template>

<style scoped>
:deep(.row-selected td) {
  background-color: rgba(24, 160, 88, 0.12);
}
</style>
