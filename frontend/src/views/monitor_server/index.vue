<script setup lang="tsx">
import { onMounted, ref } from 'vue';
import { NProgress } from 'naive-ui';
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

/** 运行秒数格式化为 Xd Xh Xm */
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

const diskColumns: DataTableColumns<DiskRow> = [
  { key: 'device', title: $t('page.monitor.server.device'), align: 'center' },
  { key: 'mountpoint', title: $t('page.monitor.server.mountpoint'), align: 'center' },
  { key: 'fstype', title: $t('page.monitor.server.fstype'), align: 'center' },
  {
    key: 'total',
    title: $t('page.monitor.server.total'),
    align: 'center',
    render: row => formatBytes(row.total)
  },
  {
    key: 'used',
    title: $t('page.monitor.server.used'),
    align: 'center',
    render: row => formatBytes(row.used)
  },
  {
    key: 'free',
    title: $t('page.monitor.server.free'),
    align: 'center',
    render: row => formatBytes(row.free)
  },
  {
    key: 'percent',
    title: $t('page.monitor.server.usage'),
    align: 'center',
    width: 140,
    render: row => (
      <NProgress type="line" percentage={row.percent} status={usageStatus(row.percent)} indicator-placement="inside" />
    )
  }
];

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
    <NCard :title="$t('page.monitor.server.title')" :bordered="false" size="small" class="card-wrapper">
      <template #header-extra>
        <NButton size="small" ghost type="primary" :disabled="loading" @click="getData">
          <template #icon>
            <icon-mdi-refresh class="text-icon" :class="{ 'animate-spin': loading }" />
          </template>
          {{ $t('page.monitor.server.refresh') }}
        </NButton>
      </template>
      <NGrid :cols="24" responsive="screen" x-gap="16" y-gap="16">
        <NFormItemGi span="24 m:12">
          <NDescriptions
            :title="$t('page.monitor.server.basic')"
            :column="1"
            label-placement="left"
            size="small"
            bordered
          >
            <NDescriptionsItem :label="$t('page.monitor.server.hostname')">
              {{ info?.os.hostname || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.osName')">
              {{ info?.os.name || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.osVersion')">
              {{ info?.os.version || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.osRelease')">
              {{ info?.os.release || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.arch')">
              {{ info?.os.machine || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.cpuModel')">
              {{ info?.os.processor || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.pythonVersion')">
              {{ info?.os.pythonVersion || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.djangoVersion')">
              {{ info?.os.djangoVersion || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.bootTime')">
              {{ info ? formatDateTime(info.os.bootTime) : '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.uptime')">
              {{ info ? formatUptime(info.os.uptime) : '-' }}
            </NDescriptionsItem>
          </NDescriptions>
        </NFormItemGi>
        <NFormItemGi span="24 m:12">
          <NDescriptions
            :title="$t('page.monitor.server.cpu')"
            :column="1"
            label-placement="left"
            size="small"
            bordered
          >
            <NDescriptionsItem :label="$t('page.monitor.server.physicalCores')">
              {{ info?.cpu.physicalCores ?? '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.logicalCores')">
              {{ info?.cpu.logicalCores ?? '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.usage')">
              <NProgress
                type="line"
                :percentage="info?.cpu.percent ?? 0"
                :status="usageStatus(info?.cpu.percent ?? 0)"
                indicator-placement="inside"
              />
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.freq')">
              {{ info ? `${info.cpu.freqCurrent} MHz / ${info.cpu.freqMax} MHz` : '-' }}
            </NDescriptionsItem>
          </NDescriptions>
        </NFormItemGi>
        <NFormItemGi span="24 m:12">
          <NDescriptions
            :title="$t('page.monitor.server.memory')"
            :column="1"
            label-placement="left"
            size="small"
            bordered
          >
            <NDescriptionsItem :label="$t('page.monitor.server.total')">
              {{ info ? formatBytes(info.memory.total) : '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.used')">
              {{ info ? formatBytes(info.memory.used) : '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.available')">
              {{ info ? formatBytes(info.memory.available) : '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.usagePercent')">
              <NProgress
                type="line"
                :percentage="info?.memory.percent ?? 0"
                :status="usageStatus(info?.memory.percent ?? 0)"
                indicator-placement="inside"
              />
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.swapTotal')">
              {{ info ? formatBytes(info.memory.swapTotal) : '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.swapUsed')">
              {{ info ? formatBytes(info.memory.swapUsed) : '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.swapUsage')">
              <NProgress
                type="line"
                :percentage="info?.memory.swapPercent ?? 0"
                :status="usageStatus(info?.memory.swapPercent ?? 0)"
                indicator-placement="inside"
              />
            </NDescriptionsItem>
          </NDescriptions>
        </NFormItemGi>
        <NFormItemGi span="24 m:12">
          <NCard :title="$t('page.monitor.server.disk')" :bordered="false" size="small" class="card-wrapper w-full">
            <NDataTable size="small" :columns="diskColumns" :data="info?.disks ?? []" />
          </NCard>
        </NFormItemGi>
        <NFormItemGi span="24 m:12">
          <NDescriptions
            :title="$t('page.monitor.server.network')"
            :column="1"
            label-placement="left"
            size="small"
            bordered
          >
            <NDescriptionsItem :label="$t('page.monitor.server.ip')">
              {{ info?.network.ip || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.bytesSent')">
              {{ info ? formatBytes(info.network.bytesSent) : '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.bytesRecv')">
              {{ info ? formatBytes(info.network.bytesRecv) : '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.packetsSent')">
              {{ info?.network.packetsSent ?? '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.server.packetsRecv')">
              {{ info?.network.packetsRecv ?? '-' }}
            </NDescriptionsItem>
          </NDescriptions>
        </NFormItemGi>
      </NGrid>
    </NCard>
  </div>
</template>

<style scoped></style>
