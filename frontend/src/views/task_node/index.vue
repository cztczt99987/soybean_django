<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import { taskNodeApi } from '@/service/api';
import { useNaivePaginatedTable } from '@/hooks/common/table';
import { defaultTransform } from '@/hooks/common/table';
import { $t } from '@/locales';
import NodeOperateDrawer from './modules/node-operate-drawer.vue';

defineOptions({ name: 'TaskNodeManage' });

const searchParams = ref<Api.Task.NodeSearchParams>({ current: 1, size: 100, name: null, status: null });

const { data: nodeList, getData: fetchNodes, loading } = useNaivePaginatedTable({
  api: () => taskNodeApi.list(searchParams.value),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    searchParams.value.current = params.page;
    searchParams.value.size = params.pageSize;
  },
  columns: () => []
});

const summary = computed(() => {
  const rows = nodeList.value || [];
  return {
    total: rows.length,
    online: rows.filter(row => row.isOnline).length,
    disabled: rows.filter(row => row.status === '0').length,
    load: rows.reduce((sum, row) => sum + (row.current_load || 0), 0)
  };
});

const drawerVisible = ref(false);
const operateType = ref<NaiveUI.TableOperateType>('add');
const editingRow = ref<Api.Task.SchedulerNode | null>(null);

function handleAdd() {
  operateType.value = 'add';
  editingRow.value = null;
  drawerVisible.value = true;
}

function handleEdit(row: Api.Task.SchedulerNode) {
  operateType.value = 'edit';
  editingRow.value = row;
  drawerVisible.value = true;
}

async function handleToggle(row: Api.Task.SchedulerNode) {
  const { error } = await taskNodeApi.toggle(row.id);
  if (!error) {
    window.$message?.success($t('common.updateSuccess'));
    fetchNodes();
  }
}

async function handleRemove(row: Api.Task.SchedulerNode) {
  await taskNodeApi.remove(row.id);
  fetchNodes();
}

function formatHeartbeat(value?: string | null) {
  if (!value) return $t('page.task.node.never');
  return value.replace('T', ' ').slice(0, 19);
}

fetchNodes();
const timer = setInterval(fetchNodes, 10000);

onUnmounted(() => {
  clearInterval(timer);
});
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <!-- 汇总卡片 -->
    <NGrid cols="2 s:4" responsive="screen" :x-gap="12" :y-gap="12">
      <NGridItem>
        <NCard :bordered="false" size="small" class="card-wrapper">
          <div class="flex-col gap-4px">
            <span class="text-12px text-gray-400">{{ $t('page.task.node.totalNodes') }}</span>
            <span class="text-24px font-600">{{ summary.total }}</span>
          </div>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard :bordered="false" size="small" class="card-wrapper">
          <div class="flex-col gap-4px">
            <span class="text-12px text-gray-400">{{ $t('page.task.node.onlineNodes') }}</span>
            <span class="text-24px font-600 text-success">{{ summary.online }}</span>
          </div>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard :bordered="false" size="small" class="card-wrapper">
          <div class="flex-col gap-4px">
            <span class="text-12px text-gray-400">{{ $t('page.task.node.disabledNodes') }}</span>
            <span class="text-24px font-600 text-warning">{{ summary.disabled }}</span>
          </div>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard :bordered="false" size="small" class="card-wrapper">
          <div class="flex-col gap-4px">
            <span class="text-12px text-gray-400">{{ $t('page.task.node.totalLoad') }}</span>
            <span class="text-24px font-600 text-info">{{ summary.load }}</span>
          </div>
        </NCard>
      </NGridItem>
    </NGrid>

    <!-- 节点列表 -->
    <NCard :title="$t('page.task.node.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <NButton size="small" ghost type="primary" @click="handleAdd">
          <template #icon>
            <icon-ic-round-plus class="text-icon" />
          </template>
          {{ $t('common.add') }}
        </NButton>
        <NButton size="small" class="ml-8px" :loading="loading" @click="fetchNodes">
          <template #icon>
            <icon-mdi-refresh class="text-icon" />
          </template>
          {{ $t('common.refresh') }}
        </NButton>
      </template>

      <NEmpty v-if="!nodeList?.length" :description="$t('common.noData')" class="py-32px" />
      <NGrid v-else cols="1 s:2 l:3 xl:4" responsive="screen" :x-gap="12" :y-gap="12">
        <NGridItem v-for="node in nodeList" :key="node.id">
          <NCard size="small" :bordered="true" class="h-full">
            <template #header>
              <div class="flex items-center gap-8px">
                <span
                  class="inline-block h-8px w-8px rounded-full"
                  :class="node.isOnline ? 'bg-success' : 'bg-gray-400'"
                />
                <span class="text-14px font-500">{{ node.name }}</span>
                <NTag v-if="node.isLocal" type="info" size="small">{{ $t('page.task.node.local') }}</NTag>
              </div>
            </template>
            <template #header-extra>
              <NTag :type="node.isOnline ? 'success' : node.status === '0' ? 'warning' : 'error'" size="small">
                {{ $t(node.isOnline ? 'page.task.node.online' : node.status === '0' ? 'page.task.node.disabled' : 'page.task.node.offline') }}
              </NTag>
            </template>
            <div class="flex-col gap-8px text-13px text-gray-500">
              <div>{{ node.host }}:{{ node.port }}</div>
              <div class="flex items-center gap-6px">
                <span>{{ $t('page.task.node.load') }}</span>
                <NProgress
                  type="line"
                  :percentage="Math.min(100, Math.round(((node.current_load || 0) / (node.max_concurrency || 1)) * 100))"
                  :show-indicator="false"
                  class="flex-1"
                />
                <span>{{ node.current_load || 0 }}/{{ node.max_concurrency }}</span>
              </div>
              <div>
                {{ $t('page.task.node.heartbeatAt') }}: {{ formatHeartbeat(node.heartbeat_at) }}
              </div>
              <div v-if="node.version">v{{ node.version }}</div>
            </div>
            <template #footer>
              <div class="flex items-center flex-wrap gap-6px">
                <NButton size="tiny" :type="node.status === '1' ? 'warning' : 'success'" ghost @click="handleToggle(node)">
                  {{ $t(node.status === '1' ? 'page.task.node.toggleDisable' : 'page.task.node.toggleEnable') }}
                </NButton>
                <NButton size="tiny" type="primary" ghost @click="handleEdit(node)">
                  {{ $t('common.edit') }}
                </NButton>
                <NPopconfirm v-if="!node.isLocal" @positive-click="handleRemove(node)">
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

      <NodeOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingRow"
        @submitted="fetchNodes"
      />
    </NCard>
  </div>
</template>
