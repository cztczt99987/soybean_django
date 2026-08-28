<script setup lang="tsx">
import { computed, onMounted, ref } from 'vue';
import { NButton, NProgress } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import dayjs from 'dayjs';
import { serverApi } from '@/service/api';
import { $t } from '@/locales';

defineOptions({ name: 'MonitorServer' });

type DiskRow = Api.Monitor.ServerInfo['disks'][number];

const loading = ref(false);
const info = ref<Api.Monitor.ServerInfo | null>(null);

/** 字节数格式化为 B/KB/MB/GB/TB（保留 2 位小数） */
function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return '0 B';
  }

  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);

  return `${(bytes / 1024 ** exponent).toFixed(2)} ${units[exponent]}`;
}

/** 秒级时间戳格式化为日期时间 */
function formatDateTime(timestamp: number): string {
  return dayjs.unix(timestamp).format('YYYY-MM-DD HH:mm:ss');
}

/** 运行秒数格式化为 X天X小时X分 */
function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  return `${days}d ${hours}h ${minutes}m`;
}

/** 使用率进度条状态 */
function usageStatus(percent: number): 'success' | 'warning' | 'error' {
  if (percent > 80) {
    return 'error';
  }
  if (percent > 60) {
    return 'warning';
  }

  return 'success';
}

/** 环形进度条颜色 */
function usageStroke(percent: number): string {
  if (percent > 80) {
    return '#d03050';
  }
  if (percent > 60) {
    return '#f0a020';
  }

  return '#18a058';
}

/** 顶部核心指标卡 */
const metricCards = computed(() => {
  if (!info.value) return [];

  return [
    {
      label: $t('page.monitor.server.usage'),
      sublabel: $t('page.monitor.server.cpu'),
      icon: 'icon-mdi-cpu-64-bit',
      color: '#2080f0',
      percent: info.value.cpu.percent,
      value: `${info.value.cpu.percent.toFixed(1)}%`,
      detail: `${info.value.cpu.logicalCores} ${$t('page.monitor.server.logicalCores')} · ${info.value.cpu.freqCurrent} MHz`
    },
    {
      label: $t('page.monitor.server.usagePercent'),
      sublabel: $t('page.monitor.server.memory'),
      icon: 'icon-mdi-memory',
      color: '#18a058',
      percent: info.value.memory.percent,
      value: `${info.value.memory.percent.toFixed(1)}%`,
      detail: `${formatBytes(info.value.memory.used)} / ${formatBytes(info.value.memory.total)}`
    },
    {
      label: $t('page.monitor.server.usage'),
      sublabel: $t('page.monitor.server.disk'),
      icon: 'icon-mdi-harddisk',
      color: '#f0a020',
      percent: info.value.diskRoot.percent,
      value: `${info.value.diskRoot.percent.toFixed(1)}%`,
      detail: `${formatBytes(info.value.diskRoot.used)} / ${formatBytes(info.value.diskRoot.total)}`
    },
    {
      label: $t('page.monitor.server.uptime'),
      sublabel: $t('page.monitor.server.basic'),
      icon: 'icon-mdi-timer-outline',
      color: '#722ed1',
      percent: Math.min(100, (info.value.os.uptime / (7 * 86400)) * 100),
      value: formatUptime(info.value.os.uptime),
      detail: formatDateTime(info.value.os.bootTime)
    }
  ];
});

const diskColumns: DataTableColumns<DiskRow> = [
  { key: 'device', title: $t('page.monitor.server.device'), align: 'center', width: 160 },
  { key: 'mountpoint', title: $t('page.monitor.server.mountpoint'), align: 'center', width: 140 },
  { key: 'fstype', title: $t('page.monitor.server.fstype'), align: 'center', width: 100 },
  {
    key: 'total',
    title: $t('page.monitor.server.total'),
    align: 'center',
    width: 110,
    render: row => formatBytes(row.total)
  },
  {
    key: 'used',
    title: $t('page.monitor.server.used'),
    align: 'center',
    width: 110,
    render: row => formatBytes(row.used)
  },
  {
    key: 'free',
    title: $t('page.monitor.server.free'),
    align: 'center',
    width: 110,
    render: row => formatBytes(row.free)
  },
  {
    key: 'percent',
    title: $t('page.monitor.server.usage'),
    align: 'center',
    width: 180,
    render: row => (
      <NProgress type="line" percentage={row.percent} status={usageStatus(row.percent)} indicator-placement="inside" />
    )
  }
];

const basicRows = computed(() => {
  if (!info.value) return [];

  return [
    { label: $t('page.monitor.server.hostname'), value: info.value.os.hostname || '-' },
    { label: $t('page.monitor.server.osName'), value: `${info.value.os.name} ${info.value.os.release}` },
    { label: $t('page.monitor.server.arch'), value: info.value.os.machine || '-' },
    { label: $t('page.monitor.server.cpuModel'), value: info.value.os.processor || '-' },
    { label: $t('page.monitor.server.pythonVersion'), value: info.value.os.pythonVersion || '-' },
    { label: $t('page.monitor.server.djangoVersion'), value: info.value.os.djangoVersion || '-' },
    { label: $t('page.monitor.server.ip'), value: info.value.network.ip || '-' },
    { label: $t('page.monitor.server.pid'), value: String(info.value.process.pid) }
  ];
});

async function getData() {
  loading.value = true;

  const { data, error } = await serverApi.info();

  if (!error) {
    info.value = data;
  } else {
    window.$message?.error(error.message);
  }

  loading.value = false;
}

onMounted(() => {
  getData();
});
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <!-- 顶部：标题 + 刷新 -->
    <NCard :bordered="false" size="small" class="card-wrapper">
      <div class="flex-center justify-between">
        <div class="flex items-center gap-12px">
          <div class="flex-center h-40px w-40px rounded-8px bg-primary bg-opacity-10">
            <icon-mdi-server-network class="text-22px text-primary" />
          </div>
          <div>
            <div class="text-16px font-600">{{ $t('page.monitor.server.title') }}</div>
            <div class="text-12px text-gray-400">
              {{ info?.os.hostname || '-' }} · {{ info?.os.name || '-' }} · {{ info?.network.ip || '-' }}
            </div>
          </div>
        </div>
        <NButton size="small" ghost type="primary" :disabled="loading" @click="getData">
          <template #icon>
            <icon-mdi-refresh class="text-icon" :class="{ 'animate-spin': loading }" />
          </template>
          {{ $t('page.monitor.server.refresh') }}
        </NButton>
      </div>
    </NCard>

    <!-- 顶部 4 张指标卡：环形进度 + 数值 + 明细 -->
    <NGrid :cols="24" responsive="screen" item-responsive :x-gap="16" :y-gap="16">
      <NGridItem v-for="card in metricCards" :key="card.sublabel" span="24 s:12 m:6">
        <NCard :bordered="false" size="small" class="card-wrapper">
          <div class="flex items-center gap-16px">
            <NProgress
              type="circle"
              :percentage="Math.round(card.percent)"
              :stroke-width="8"
              :show-indicator="false"
              :color="usageStroke(card.percent)"
              rail-color="rgba(128,128,128,0.15)"
              class="shrink-0"
            >
              <div class="text-center">
                <div class="text-14px font-600" :style="{ color: usageStroke(card.percent) }">
                  {{ Math.round(card.percent) }}%
                </div>
              </div>
            </NProgress>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-6px text-13px text-gray-500">
                <span :class="card.icon" class="text-16px" :style="{ color: card.color }" />
                <span>{{ card.sublabel }}</span>
              </div>
              <div class="mt-4px truncate text-20px font-700">{{ card.value }}</div>
              <div class="mt-2px truncate text-12px text-gray-400" :title="card.detail">{{ card.detail }}</div>
            </div>
          </div>
        </NCard>
      </NGridItem>
    </NGrid>

    <!-- 中部：基本信息 + 内存/Swap 明细 -->
    <NGrid :cols="24" responsive="screen" item-responsive :x-gap="16" :y-gap="16">
      <NGridItem span="24 m:14">
        <NCard :title="$t('page.monitor.server.basic')" :bordered="false" size="small" class="card-wrapper">
          <NDescriptions :column="2" label-placement="left" size="small" bordered>
            <NDescriptionsItem v-for="row in basicRows" :key="row.label" :label="row.label">
              <span class="break-all">{{ row.value }}</span>
            </NDescriptionsItem>
          </NDescriptions>
        </NCard>
      </NGridItem>
      <NGridItem span="24 m:10">
        <NCard :title="$t('page.monitor.server.memory')" :bordered="false" size="small" class="card-wrapper">
          <NSpace vertical :size="20" class="py-4px">
            <div>
              <div class="mb-6px flex items-center justify-between text-13px">
                <span>RAM</span>
                <span class="text-gray-400">
                  {{ info ? formatBytes(info.memory.used) : '-' }} / {{ info ? formatBytes(info.memory.total) : '-' }}
                </span>
              </div>
              <NProgress
                type="line"
                :height="10"
                :percentage="info?.memory.percent ?? 0"
                :status="usageStatus(info?.memory.percent ?? 0)"
                indicator-placement="inside"
              />
            </div>
            <div>
              <div class="mb-6px flex items-center justify-between text-13px">
                <span>Swap</span>
                <span class="text-gray-400">
                  {{ info ? formatBytes(info.memory.swapUsed) : '-' }} /
                  {{ info ? formatBytes(info.memory.swapTotal) : '-' }}
                </span>
              </div>
              <NProgress
                type="line"
                :height="10"
                :percentage="info?.memory.swapPercent ?? 0"
                :status="usageStatus(info?.memory.swapPercent ?? 0)"
                indicator-placement="inside"
              />
            </div>
            <NDescriptions :column="2" label-placement="left" size="small">
              <NDescriptionsItem :label="$t('page.monitor.server.available')">
                {{ info ? formatBytes(info.memory.available) : '-' }}
              </NDescriptionsItem>
              <NDescriptionsItem :label="$t('page.monitor.server.freq')">
                {{ info ? `${info.cpu.freqCurrent} MHz` : '-' }}
              </NDescriptionsItem>
              <NDescriptionsItem :label="$t('page.monitor.server.physicalCores')">
                {{ info?.cpu.physicalCores ?? '-' }}
              </NDescriptionsItem>
              <NDescriptionsItem :label="$t('page.monitor.server.logicalCores')">
                {{ info?.cpu.logicalCores ?? '-' }}
              </NDescriptionsItem>
              <NDescriptionsItem :label="$t('page.monitor.server.bytesSent')">
                {{ info ? formatBytes(info.network.bytesSent) : '-' }}
              </NDescriptionsItem>
              <NDescriptionsItem :label="$t('page.monitor.server.bytesRecv')">
                {{ info ? formatBytes(info.network.bytesRecv) : '-' }}
              </NDescriptionsItem>
            </NDescriptions>
          </NSpace>
        </NCard>
      </NGridItem>
    </NGrid>

    <!-- 底部：磁盘分区表 -->
    <NCard :title="$t('page.monitor.server.disk')" :bordered="false" size="small" class="card-wrapper">
      <NDataTable size="small" :columns="diskColumns" :data="info?.disks ?? []" :bordered="false" />
    </NCard>
  </div>
</template>

<style scoped></style>
