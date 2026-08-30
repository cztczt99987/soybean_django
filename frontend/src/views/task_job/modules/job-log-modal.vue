<script setup lang="tsx">
import { ref, watch } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import { execStatusTagType } from '@/constants/task';
import { taskJobApi } from '@/service/api';
import { defaultTransform, useNaivePaginatedTable } from '@/hooks/common/table';
import { $t } from '@/locales';

defineOptions({ name: 'TaskJobLogModal' });

interface Props {
  jobId?: number | null;
  jobName?: string;
}

const props = defineProps<Props>();

const visible = defineModel<boolean>('visible', { default: false });

const searchParams = ref<Api.Task.LogSearchParams>({ current: 1, size: 10, job: undefined, status: null });

const { columns, data, getData, loading, pagination } = useNaivePaginatedTable({
  api: () => taskJobApi.logs(props.jobId || 0, searchParams.value),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    searchParams.value.current = params.page;
    searchParams.value.size = params.pageSize;
  },
  columns: (): NaiveUI.TableColumn<Api.Task.ExecutionLog>[] => [
    {
      key: 'started_at',
      title: $t('page.task.job.startedAt'),
      align: 'center',
      width: 170,
      render: row => row.started_at?.replace('T', ' ').slice(0, 19) || '-'
    },
    {
      key: 'status',
      title: $t('page.task.job.execStatus'),
      align: 'center',
      width: 90,
      render: row => <NTag type={execStatusTagType[row.status]} size="small">{row.status}</NTag>
    },
    {
      key: 'duration_ms',
      title: $t('page.task.job.duration'),
      align: 'center',
      width: 100,
      render: row => `${row.duration_ms} ms`
    },
    {
      key: 'node_name',
      title: $t('page.task.job.node'),
      align: 'center',
      width: 160,
      render: row => row.node_name || '-'
    },
    {
      key: 'result',
      title: $t('page.task.job.output'),
      align: 'center',
      width: 120,
      render: row =>
        (row.error_msg || row.output) && (
          <NPopconfirm>
            {{
              default: () => (
                <pre class="max-w-480px max-h-300px overflow-auto whitespace-pre-wrap text-left">{row.error_msg || row.output}</pre>
              ),
              trigger: () => (
                <NButton text type="primary" size="small">
                  {$t('page.task.job.viewDetail')}
                </NButton>
              )
            }}
          </NPopconfirm>
        ) || '-'
    }
  ]
});

watch(visible, val => {
  if (val && props.jobId) {
    getData();
  }
});
</script>

<template>
  <NModal v-model:show="visible" preset="card" class="w-860px" :title="`${jobName || ''} - ${$t('page.task.job.logTitle')}`">
    <div class="flex-col gap-12px">
      <NSpace justify="end">
        <NButton size="small" @click="getData">
          <template #icon>
            <icon-ic-round-refresh class="text-icon" />
          </template>
          {{ $t('common.refresh') }}
        </NButton>
      </NSpace>
      <NDataTable
        :columns="columns"
        :data="data"
        size="small"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="pagination"
        :scroll-x="760"
        max-height="420"
      />
    </div>
  </NModal>
</template>
