<script setup lang="tsx">
import { ref } from 'vue';
import { NButton, NPopconfirm, NSwitch } from 'naive-ui';
import { userGenderRecord } from '@/constants/business';
import { userApi } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { $t } from '@/locales';
import UserOperateDrawer from './modules/user-operate-drawer.vue';
import UserSearch from './modules/user-search.vue';

const appStore = useAppStore();

const searchParams = ref<Api.System.UserSearchParams>({
  current: 1,
  size: 10,
  keyword: null,
  username: null,
  nickname: null,
  phone: null,
  status: null,
  deptId: null
});

const { columns, columnChecks, data, getData, getDataByPage, loading, mobilePagination } = useNaivePaginatedTable({
  api: () => userApi.list(searchParams.value),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    searchParams.value.current = params.page;
    searchParams.value.size = params.pageSize;
  },
  columns: () => [
    {
      type: 'selection',
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
      title: $t('page.system.user.form.username'),
      align: 'center',
      width: 120
    },
    {
      key: 'nickname',
      title: $t('page.system.user.form.nickname'),
      align: 'center',
      width: 120
    },
    {
      key: 'dept.name',
      title: $t('page.system.user.form.dept'),
      align: 'center',
      width: 120,
      render: row => row.dept?.name ?? '-'
    },
    {
      key: 'phone',
      title: $t('page.system.user.form.phone'),
      align: 'center',
      width: 140
    },
    {
      key: 'email',
      title: $t('page.system.user.form.email'),
      align: 'center',
      width: 180
    },
    {
      key: 'gender',
      title: $t('page.system.user.form.gender'),
      align: 'center',
      width: 80,
      render: row => $t(userGenderRecord[row.gender])
    },
    {
      key: 'status',
      title: $t('page.system.user.form.status'),
      align: 'center',
      width: 120,
      render: row => (
        <NSwitch value={row.status === '1'} onUpdateValue={(val: boolean) => handleChangeStatus(row.id, val)}>
          {{
            checked: () => $t('page.system.common.enabled'),
            unchecked: () => $t('page.system.common.disabled')
          }}
        </NSwitch>
      )
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
      width: 240,
      fixed: 'right',
      render: row => (
        <div class="flex-center gap-8px">
          <NButton size="small" type="warning" ghost onClick={() => handleResetPwd(row.id)}>
            {$t('page.system.user.action.resetPwd')}
          </NButton>
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

const { drawerVisible, operateType, editingData, handleAdd, handleEdit, checkedRowKeys, onBatchDeleted, onDeleted } =
  useTableOperate(data, 'id', getData);

async function handleBatchDelete() {
  await userApi.batchDelete(checkedRowKeys.value.map(Number));

  onBatchDeleted();
}

async function handleDelete(id: number) {
  await userApi.remove(id);

  onDeleted();
}

function edit(id: number) {
  handleEdit(id);
}

async function handleChangeStatus(id: number, val: boolean) {
  const { error } = await userApi.changeStatus(id, val ? '1' : '0');

  if (!error) {
    window.$message?.success($t('page.system.common.changeStatusSuccess'));

    await getData();
  }
}

function handleResetPwd(id: number) {
  window.$dialog?.warning({
    title: $t('common.tip'),
    content: $t('page.system.common.resetPwdConfirm'),
    positiveText: $t('common.confirm'),
    negativeText: $t('common.cancel'),
    onPositiveClick: async () => {
      const { error } = await userApi.resetPwd(id);

      if (!error) {
        window.$message?.success($t('page.system.common.resetPwdSuccess'));
      }
    }
  });
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <UserSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard :title="$t('page.system.user.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          @add="handleAdd"
          @delete="handleBatchDelete"
          @refresh="getData"
        />
      </template>
      <NDataTable
        v-model:checked-row-keys="checkedRowKeys"
        :columns="columns"
        :data="data"
        size="small"
        :flex-height="!appStore.isMobile"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        :scroll-x="1412"
        class="sm:h-full"
      />
      <UserOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getDataByPage"
      />
    </NCard>
  </div>
</template>
