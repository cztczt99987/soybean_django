<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import { taskJobApi, taskLogApi, schedulerApi } from '@/service/api';
import { defaultTransform, useNaivePaginatedTable } from '@/hooks/common/table';
import { $t } from '@/locales';
import SchedulerConsoleModal from './modules/scheduler-console-modal.vue';

defineOptions({ name: 'TaskSchedulerMonitor' });

/** ============ 调度器状态 ============ */
const status = ref<Api.Task.SchedulerStatus>();
const consoleVisible = ref(false);

async function fetchStatus() {
  const { data, error } = await schedulerApi.status();
  if (!error) {
    status.value = data;
  }
}

const stateTagType = computed(() => {
  switch (status.value?.state) {
    case 'running':
      return 'success';
    case 'paused':
      return 'warning';
    default:
      return 'error';
  }
});

const stateLabel = computed(() => {
  const s = status.value?.state || 'stopped';
  return $t(`page.task.scheduler.state${s.charAt(0).toUpperCase()}${s.slice(1)}` as App.I18n.I18nKey);
});

function formatUptime(seconds: number) {
  if (!seconds) return '-';
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m ${s}s`;
  return `${m}m ${s}s`;
}

/** ============ 任务卡片列表 ============ */
const jobName = ref<string | null>(null);
const jobStatus = ref<Api.Task.TaskStatus | null>(null);

const searchParams = ref<Api.Task.TaskJobSearchParams>({ current: 1, size: 100, name: null, status: null });

const { data: jobList, getData: fetchJobs, loading: jobLoading } = useNaivePaginatedTable({
  api: () => taskJobApi.list(searchParams.value),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    searchParams.value.current = params.page;
    searchParams.value.size = params.pageSize;
  },
  columns: () => []
});

const filteredJobs = computed(() => {
  let rows = jobList.value || [];
  if (jobName.value) {
    rows = rows.filter(row => row.name.includes(jobName.value as string));
  }
  if (jobStatus.value) {
    rows = rows.filter(row => row.status === jobStatus.value);
  }
  return rows;
});

function handleSearch() {
  searchParams.value.name = jobName.value;
  searchParams.value.status = jobStatus.value;
  fetchJobs();
}

function handleReset() {
  jobName.value = null;
  jobStatus.value = null;
  handleSearch();
}

/** ============ 调度器控制 ============ */
async function handleControl(action: string) {
  const { error } = await schedulerApi.control(action);
  if (!error) {
    window.$message?.success($t('common.updateSuccess'));
    refreshAll();
  }
}

/** ============ 任务卡片操作 ============ */
const drawerVisible = ref(false);
const operateType = ref<NaiveUI.TableOperateType>('add');
const editingRow = ref<Api.Task.TaskJob | null>(null);

function openEdit(row: Api.Task.TaskJob) {
  operateType.value = 'edit';
  editingRow.value = row;
  drawerVisible.value = true;
}

async function handleJobPause(row: Api.Task.TaskJob) {
  const { error } = await taskJobApi.pause(row.id);
  if (!error) {
    window.$message?.success($t('common.updateSuccess'));
    refreshAll();
  }
}

async function handleJobResume(row: Api.Task.TaskJob) {
  const { error } = await taskJobApi.resume(row.id);
  if (!error) {
    window.$message?.success($t('common.updateSuccess'));
    refreshAll();
  }
}

async function handleTest(row: Api.Task.TaskJob) {
  const { error } = await taskJobApi.runOnce(row.id);
  if (!error) {
    window.$message?.success($t('page.task.job.runOnceSent'));
    setTimeout(refreshAll, 1500);
  }
}

async function handleRemove(id: number) {
  await taskJobApi.remove(id);
  refreshAll();
}

/** ============ 最近执行日志 ============ */
const recentLogs = ref<Api.Task.ExecutionLog[]>([]);

async function fetchRecentLogs() {
  const { data, error } = await taskLogApi.list({ current: 1, size: 8 });
  if (!error) {
    recentLogs.value = data?.records || [];
  }
}

function refreshAll() {
  fetchStatus();
  fetchJobs();
  fetchRecentLogs();
}

refreshAll();
const statusTimer = setInterval(fetchStatus, 5000);
const logTimer = setInterval(fetchRecentLogs, 5000);

onUnmounted(() => {
  clearInterval(statusTimer);
  clearInterval(logTimer);
});
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <!-- 异常报警横幅 -->
    <NAlert v-if="status && (status.alerts.length > 0 || status.state !== 'running')" type="warning" :bordered="false" class="banner">
      {{ $t('page.task.scheduler.alertBanner', { count: status.alerts.length }) }}
    </NAlert>
    <NAlert v-else-if="status" type="info" :bordered="false" class="banner" :show-icon="false">
      {{ $t('page.task.scheduler.normalBanner') }}
    </NAlert>

    <!-- 搜索栏 -->
    <NCard :bordered="false" size="small" class="card-wrapper">
      <form class="flex items-center flex-wrap gap-16px" @submit.prevent="handleSearch">
        <div class="flex items-center gap-8px">
          <span class="whitespace-nowrap text-14px">{{ $t('page.task.job.name') }}</span>
          <NInput
            v-model:value="jobName"
            class="w-220px"
            size="small"
            clearable
            :placeholder="$t('page.task.job.namePlaceholder')"
            @keyup.enter="handleSearch"
          />
        </div>
        <div class="flex items-center gap-8px">
          <span class="whitespace-nowrap text-14px">{{ $t('page.task.job.status') }}</span>
          <NSelect
            v-model:value="jobStatus"
            class="w-180px"
            size="small"
            clearable
            :options="[
              { label: $t('page.task.scheduler.cardRunning'), value: '1' },
              { label: $t('page.task.scheduler.cardPaused'), value: '0' }
            ]"
            :placeholder="$t('page.task.job.statusPlaceholder')"
          />
        </div>
        <div class="flex-1" />
        <NSpace :size="8">
          <NButton size="small" @click="handleReset">
            <template #icon>
              <icon-ic-round-refresh class="text-icon" />
            </template>
            {{ $t('common.reset') }}
          </NButton>
          <NButton size="small" type="primary" attr-type="submit">
            <template #icon>
              <icon-ic-round-search class="text-icon" />
            </template>
            {{ $t('common.search') }}
          </NButton>
        </NSpace>
      </form>
    </NCard>

    <!-- 调度器控制栏 -->
    <NCard :bordered="false" size="small" class="card-wrapper">
      <div class="flex items-center flex-wrap gap-12px">
        <NSpace :size="8" align="center">
          <span class="text-14px font-500">{{ $t('page.task.scheduler.scheduler') }}</span>
          <NTag v-if="status" :type="stateTagType" size="small" round>
            {{ stateLabel }}
          </NTag>
        </NSpace>
        <NDivider vertical />
        <NSpace :size="8" align="center">
          <span class="text-14px">{{ $t('page.task.scheduler.nodesOnline') }}</span>
          <NTag type="success" size="small" round>
            {{ status?.nodeOnlineCount || 0 }} / {{ status?.nodeCount || 0 }}
          </NTag>
        </NSpace>
        <NDivider vertical />
        <NSpace :size="8" align="center">
          <span class="text-14px">{{ $t('page.task.scheduler.tasks') }}</span>
          <NTag type="warning" size="small" round>{{ filteredJobs.length }}</NTag>
        </NSpace>
        <div class="flex-1" />
        <NSpace :size="8">
          <NButton size="small" type="success" :disabled="status?.state === 'running'" @click="handleControl('start')">
            <template #icon>
              <icon-ic-round-play-arrow class="text-icon" />
            </template>
            {{ $t('page.task.scheduler.start') }}
          </NButton>
          <NButton size="small" type="warning" :disabled="status?.state !== 'running'" @click="handleControl('pause')">
            <template #icon>
              <icon-ic-round-pause class="text-icon" />
            </template>
            {{ $t('page.task.scheduler.pause') }}
          </NButton>
          <NButton size="small" type="primary" :disabled="status?.state !== 'paused'" @click="handleControl('resume')">
            <template #icon>
              <icon-ic-round-refresh class="text-icon" />
            </template>
            {{ $t('page.task.scheduler.resume') }}
          </NButton>
          <NPopconfirm @positive-click="handleControl('shutdown')">
            <template #trigger>
              <NButton size="small" type="error" :disabled="status?.state === 'stopped'">
                <template #icon>
                  <icon-ic-round-power-settings-new class="text-icon" />
                </template>
                {{ $t('page.task.scheduler.shutdown') }}
              </NButton>
            </template>
            {{ $t('page.task.scheduler.shutdownConfirm') }}
          </NPopconfirm>
          <NPopconfirm @positive-click="handleControl('clear')">
            <template #trigger>
              <NButton size="small" type="error" ghost :disabled="status?.state === 'stopped'">
                {{ $t('page.task.scheduler.clearJobs') }}
              </NButton>
            </template>
            {{ $t('page.task.scheduler.clearConfirm') }}
          </NPopconfirm>
          <NButton size="small" color="#363636" @click="consoleVisible = true">
            <template #icon>
              <icon-ic-round-terminal class="text-icon" />
            </template>
            {{ $t('page.task.scheduler.console') }}
          </NButton>
          <NButton size="small" type="primary" circle :loading="jobLoading" @click="refreshAll">
            <template #icon>
              <icon-ic-round-refresh class="text-icon" />
            </template>
          </NButton>
        </NSpace>
      </div>
    </NCard>

    <!-- 任务卡片 -->
    <NGrid v-if="filteredJobs.length" cols="1 s:2 l:3 xl:4" responsive="screen" :x-gap="12" :y-gap="12">
      <NGridItem v-for="job in filteredJobs" :key="job.id">
        <NCard size="small" :bordered="true" class="h-full">
          <template #header>
            <div class="flex items-center gap-8px">
              <span
                class="inline-block h-8px w-8px rounded-full"
                :class="job.isRunning ? 'bg-success' : 'bg-warning'"
              />
              <span class="text-14px font-500">{{ job.name }}</span>
              <NTag :type="job.isRunning ? 'success' : 'warning'" size="small">
                {{ $t(job.isRunning ? 'page.task.scheduler.cardRunning' : 'page.task.scheduler.cardPaused') }}
              </NTag>
            </div>
          </template>
          <div class="flex-col gap-8px text-13px text-gray-500">
            <div class="flex items-center gap-6px">
              <icon-ic-round-schedule class="text-icon text-14px" />
              <span>{{ job.triggerDesc }}</span>
            </div>
            <div class="flex items-center gap-6px">
              <icon-ic-round-access-time class="text-icon text-14px" />
              <span>{{ job.next_run_at ? job.next_run_at.replace('T', ' ').slice(0, 19) : $t('page.task.scheduler.noNextRun') }}</span>
            </div>
          </div>
          <template #footer>
            <div class="flex items-center flex-wrap gap-6px">
              <NButton v-if="job.status === '1'" size="tiny" type="warning" ghost @click="handleJobPause(job)">
                {{ $t('page.task.scheduler.pause') }}
              </NButton>
              <NButton v-else size="tiny" type="success" ghost @click="handleJobResume(job)">
                {{ $t('page.task.scheduler.resume') }}
              </NButton>
              <NButton size="tiny" type="success" ghost @click="handleTest(job)">
                {{ $t('page.task.scheduler.test') }}
              </NButton>
              <NButton size="tiny" type="primary" ghost @click="openEdit(job)">
                {{ $t('common.edit') }}
              </NButton>
              <NPopconfirm @positive-click="handleRemove(job.id)">
                <template #trigger>
                  <NButton size="tiny" type="error" ghost>
                    {{ $t('common.delete') }}
                  </NButton>
                </template>
                {{ $t('common.confirmDelete') }}
              </NPopconfirm>
            </div>
          </template>
        </NCard>
      </NGridItem>
    </NGrid>
    <NCard v-else :bordered="false" size="small">
      <NEmpty :description="$t('common.noData')" class="py-24px" />
    </NCard>

    <!-- 监控指标 -->
    <NCard :title="$t('page.task.scheduler.metricsTitle')" :bordered="false" size="small" class="card-wrapper">
      <NGrid cols="2 s:4 l:6 xl:8" responsive="screen" :x-gap="12" :y-gap="12">
        <NGridItem>
          <div class="flex-col gap-4px rounded-4px bg-primary-50 dark:bg-[#1b2437] p-12px">
            <span class="text-12px text-gray-400">{{ $t('page.task.scheduler.state') }}</span>
            <NTag :type="stateTagType" size="small" class="w-fit">
              {{ stateLabel }}
            </NTag>
          </div>
        </NGridItem>
        <NGridItem>
          <div class="flex-col gap-4px rounded-4px bg-primary-50 dark:bg-[#1b2437] p-12px">
            <span class="text-12px text-gray-400">{{ $t('page.task.scheduler.uptime') }}</span>
            <span class="text-18px font-600">{{ formatUptime(status?.uptime || 0) }}</span>
          </div>
        </NGridItem>
        <NGridItem>
          <div class="flex-col gap-4px rounded-4px bg-primary-50 dark:bg-[#1b2437] p-12px">
            <span class="text-12px text-gray-400">CPU</span>
            <span class="text-18px font-600">{{ status?.process?.cpuPercent?.toFixed(1) || 0 }}%</span>
          </div>
        </NGridItem>
        <NGridItem>
          <div class="flex-col gap-4px rounded-4px bg-primary-50 dark:bg-[#1b2437] p-12px">
            <span class="text-12px text-gray-400">{{ $t('page.task.scheduler.mem') }}</span>
            <span class="text-18px font-600">{{ status?.process?.memPercent?.toFixed(1) || 0 }}%</span>
          </div>
        </NGridItem>
        <NGridItem>
          <div class="flex-col gap-4px rounded-4px bg-primary-50 dark:bg-[#1b2437] p-12px">
            <span class="text-12px text-gray-400">{{ $t('page.task.scheduler.todayTotal') }}</span>
            <span class="text-18px font-600">{{ status?.metrics?.todayTotal || 0 }}</span>
          </div>
        </NGridItem>
        <NGridItem>
          <div class="flex-col gap-4px rounded-4px bg-primary-50 dark:bg-[#1b2437] p-12px">
            <span class="text-12px text-gray-400">{{ $t('page.task.scheduler.successRate') }}</span>
            <span class="text-18px font-600 text-success">{{ status?.metrics?.successRate || 0 }}%</span>
          </div>
        </NGridItem>
        <NGridItem>
          <div class="flex-col gap-4px rounded-4px bg-primary-50 dark:bg-[#1b2437] p-12px">
            <span class="text-12px text-gray-400">{{ $t('page.task.scheduler.avgDuration') }}</span>
            <span class="text-18px font-600">{{ status?.metrics?.avgDurationMs || 0 }} ms</span>
          </div>
        </NGridItem>
        <NGridItem>
          <div class="flex-col gap-4px rounded-4px bg-primary-50 dark:bg-[#1b2437] p-12px">
            <span class="text-12px text-gray-400">{{ $t('page.task.scheduler.todayFailed') }}</span>
            <span class="text-18px font-600" :class="(status?.metrics?.todayFailed || 0) > 0 ? 'text-error' : ''">
              {{ status?.metrics?.todayFailed || 0 }}
            </span>
          </div>
        </NGridItem>
      </NGrid>
    </NCard>

    <!-- 异常报警 + 最近执行 -->
    <NGrid cols="1 l:2" responsive="screen" :x-gap="12" :y-gap="12">
      <NGridItem>
        <NCard :title="$t('page.task.scheduler.alerts')" :bordered="false" size="small" class="card-wrapper">
          <NEmpty v-if="!status?.alerts?.length" :description="$t('page.task.scheduler.alertsEmpty')" class="py-24px" />
          <div v-else class="flex-col gap-8px">
            <div
              v-for="alert in status.alerts"
              :key="alert.id"
              class="rounded-4px border border-warning-200 bg-warning-50 dark:bg-[#2b241b] p-8px text-13px"
            >
              <div class="flex items-center gap-8px">
                <NTag type="error" size="tiny">{{ alert.status }}</NTag>
                <span class="font-500">{{ alert.jobName }}</span>
                <span class="text-gray-400">{{ alert.startedAt }}</span>
              </div>
              <div class="mt-4px line-clamp-2 text-gray-500">{{ alert.error }}</div>
            </div>
          </div>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard :title="$t('page.task.scheduler.recentLogs')" :bordered="false" size="small" class="card-wrapper">
          <NEmpty v-if="!recentLogs.length" :description="$t('common.noData')" class="py-24px" />
          <div v-else class="flex-col gap-8px">
            <div
              v-for="log in recentLogs"
              :key="log.id"
              class="flex items-center gap-8px text-13px"
            >
              <NTag :type="log.status === 'success' ? 'success' : log.status === 'running' ? 'info' : 'error'" size="tiny">
                {{ log.status }}
              </NTag>
              <span class="font-500">{{ log.job_name }}</span>
              <span class="text-gray-400">{{ log.duration_ms }}ms</span>
              <span class="ml-auto text-gray-400">{{ log.started_at?.replace('T', ' ').slice(0, 19) }}</span>
            </div>
          </div>
        </NCard>
      </NGridItem>
    </NGrid>

    <SchedulerConsoleModal v-model:visible="consoleVisible" />
  </div>
</template>

<style scoped>
.banner {
  --n-padding: 8px 14px;
}
</style>
