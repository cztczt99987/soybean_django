<script setup lang="ts">
import { onUnmounted, ref, watch } from 'vue';
import { schedulerApi } from '@/service/api';
import { $t } from '@/locales';

defineOptions({ name: 'SchedulerConsoleModal' });

const visible = defineModel<boolean>('visible', { default: false });

const keyword = ref('');
const logs = ref<Api.Task.ConsoleLog[]>([]);
let timer: ReturnType<typeof setInterval> | null = null;

const levelColor: Record<string, string> = {
  info: '#4ade80',
  warn: '#facc15',
  error: '#f87171'
};

async function fetchLogs() {
  const { data, error } = await schedulerApi.console(keyword.value || undefined);
  if (!error) {
    logs.value = data || [];
  }
}

function startPolling() {
  fetchLogs();
  stopPolling();
  timer = setInterval(fetchLogs, 3000);
}

function stopPolling() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

watch(visible, val => {
  if (val) {
    startPolling();
  } else {
    stopPolling();
  }
});

onUnmounted(stopPolling);
</script>

<template>
  <NModal v-model:show="visible" preset="card" class="w-780px" :title="$t('page.task.scheduler.consoleTitle')">
    <div class="flex-col gap-12px">
      <NSpace justify="end">
        <NInput
          v-model:value="keyword"
          size="small"
          class="w-240px"
          clearable
          :placeholder="$t('page.task.scheduler.keyword')"
          @keyup.enter="fetchLogs"
        />
        <NButton size="small" @click="fetchLogs">
          <template #icon>
            <icon-ic-round-refresh class="text-icon" />
          </template>
          {{ $t('common.refresh') }}
        </NButton>
      </NSpace>
      <div class="h-400px overflow-auto rounded-4px bg-[#0d1117] p-12px font-mono text-13px leading-22px">
        <div v-if="logs.length === 0" class="text-center text-gray-500">{{ $t('common.noData') }}</div>
        <div v-for="(log, index) in logs" :key="index" :style="{ color: levelColor[log.level] || '#8b949e' }">
          [{{ log.time }}] [{{ log.level.toUpperCase() }}] {{ log.msg }}
        </div>
      </div>
      <div class="text-right text-12px text-gray-400">{{ $t('page.task.scheduler.consoleTip') }}</div>
    </div>
  </NModal>
</template>
