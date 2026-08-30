<script setup lang="tsx">
import { ref } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import { enableStatusRecord } from '@/constants/business';
import { execStatusTagType, taskPriorityRecord } from '@/constants/task';
import { taskJobApi } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { $t } from '@/locales';
import JobLogModal from './modules/job-log-modal.vue';
import JobOperateDrawer from './modules/job-operate-drawer.vue';
import JobSearch from './modules/job-search.vue';

const appStore = useAppStore();

const searchParams = ref<Api.Task.TaskJobSearchParams>({
  current: 1,
  size: 10,
  name: null,
  status: null,
  trigger_type: null
});

const { columns, columnChecks, data, getData, getDataByPage, loading, mobilePagination } = useNaivePaginatedTable({
  api: () => taskJobApi.list(searchParams.value),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    searchParams.value.current = params.page;
    searchParams.value.size = params.pageSize;
  },
  columns: () => [
    {
      key: 'index',
      title: $t('common.index'),
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'name',
      title: $t('page.task.job.name'),
      align: 'center',
      width: 150
    },
    {
      key: 'description',
      title: $t('page.task.job.description'),
      align: 'center',
      width: 180,
      ellipsis: { tooltip: true }
    },
    {
      key: 'job_type',
      title: $t('page.task.job.jobType'),
      align: 'center',
      width: 90,
      render: row => $t(row.job_type === 'http' ? 'page.task.job.typeHttp' : 'page.task.job.typeFunction')
    },
    {
      key: 'trigger_type',
      title: $t('page.task.job.triggerType'),
      align: 'center',
      width: 130,
      render: row => (
        <div class="flex-col">
          <span>{$t(`page.task.job.trigger${row.trigger_type.charAt(0).toUpperCase()}${row.trigger_type.slice(1)}` as App.I18n.I18nKey)}</span>
          <span class="text-12px text-gray-400">{row.triggerDesc}</span>
        </div>
      )
    },
    {
      key: 'priority',
      title: $t('page.task.job.priority'),
      align: 'center',
      width: 80,
      render: row => {
        const tagMap: Record<string, NaiveUI.ThemeColor> = { '1': 'error', '2': 'warning', '3': 'default' };
        return <NTag type={tagMap[row.priority]} size="small">{$t(taskPriorityRecord[row.priority])}</NTag>;
      }
    },
    {
      key: 'status',
      title: $t('page.task.job.status'),
      align: 'center',
      width: 80,
      render: row => {
        const tagMap: Record<string, NaiveUI.ThemeColor> = { '1': 'success', '0': 'warning' };
        return <NTag type={tagMap[row.status]} size="small">{$t(enableStatusRecord[row.status])}</NTag>;
      }
    },
    {
      key: 'next_run_at',
      title: $t('page.task.job.nextRunAt'),
      align: 'center',
      width: 160,
      render: row => (row.next_run_at ? row.next_run_at.replace('T', ' ').slice(0, 19) : '-')
    },
    {
      key: 'last_run_at',
      title: $t('page.task.job.lastRunAt'),
      align: 'center',
      width: 160,
      render: row => {
        if (!row.last_run_at) return '-';
        const status = row.last_status as keyof typeof execStatusTagType;
        return (
          <div class="flex-col">
            <span>{row.last_run_at.replace('T', ' ').slice(0, 19)}</span>
            {row.last_status && (
              <NTag type={execStatusTagType[status] || 'default'} size="tiny">
                {row.last_status}
              </NTag>
            )}
          </div>
        );
      }
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 300,
      fixed: 'right',
      render: row => (
        <div class="flex-center flex-wrap gap-6px">
          <NButton type="primary" ghost size="small" onClick={() => openLogs(row)}>
            {$t('page.task.job.logs')}
          </NButton>
          <NButton type="info" ghost size="small" onClick={() => handleRunOnce(row.id)}>
            {$t('page.task.job.runOnce')}
          </NButton>
          {row.status === '1' ? (
            <NPopconfirm onPositiveClick={() => handlePause(row.id)}>
              {{
                default: () => $t('page.task.job.pauseConfirm'),
                trigger: () => (
                  <NButton type="warning" ghost size="small">
                    {$t('page.task.job.pause')}
                  </NButton>
                )
              }}
            </NPopconfirm>
          ) : (
            <NButton type="success" ghost size="small" onClick={() => handleResume(row.id)}>
              {$t('page.task.job.resume')}
            </NButton>
          )}
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

const { drawerVisible, operateType, editingData, handleAdd, handleEdit, onDeleted } = useTableOperate(data, 'id', getData);

/** 执行历史弹窗 */
const logVisible = ref(false);
const logJobId = ref<number | null>(null);
const logJobName = ref('');

function openLogs(row: Api.Task.TaskJob) {
  logJobId.value = row.id;
  logJobName.value = row.name;
  logVisible.value = true;
}

async function handleRunOnce(id: number) {
  const { error } = await taskJobApi.runOnce(id);
  if (!error) {
    window.$message?.success($t('page.task.job.runOnceSent'));
    setTimeout(() => getData(), 1500);
  }
}

async function handlePause(id: number) {
  const { error } = await taskJobApi.pause(id);
  if (!error) {
    window.$message?.success($t('common.updateSuccess'));
    getData();
  }
}

async function handleResume(id: number) {
  const { error } = await taskJobApi.resume(id);
  if (!error) {
    window.$message?.success($t('common.updateSuccess'));
    getData();
  }
}

async function handleDelete(id: number) {
  await taskJobApi.remove(id);
  onDeleted();
}

function edit(id: number) {
  handleEdit(id);
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <JobSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard :title="$t('page.task.job.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <TableHeaderOperation v-model:columns="columnChecks" :loading="loading" @refresh="getData">
          <template #default>
            <NButton size="small" ghost type="primary" @click="handleAdd">
              <template #icon>
                <icon-ic-round-plus class="text-icon" />
              </template>
              {{ $t('common.add') }}
            </NButton>
          </template>
        </TableHeaderOperation>
      </template>
      <NDataTable
        :columns="columns"
        :data="data"
        size="small"
        :flex-height="!appStore.isMobile"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        :scroll-x="1400"
        class="sm:h-full"
      />
      <JobOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getDataByPage"
      />
      <JobLogModal v-model:visible="logVisible" :job-id="logJobId" :job-name="logJobName" />
    </NCard>
  </div>
</template>
