<script setup lang="tsx">
import { ref } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import type { DataScope, EnableStatus } from '@/constants/business';
import { dataScopeRecord, enableStatusRecord } from '@/constants/business';
import { menuApi, roleApi } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { $t } from '@/locales';
import RoleOperateDrawer from './modules/role-operate-drawer.vue';
import RoleSearch from './modules/role-search.vue';

const appStore = useAppStore();

const searchParams = ref<Api.System.RoleSearchParams>({
  current: 1,
  size: 10,
  keyword: null,
  name: null,
  code: null,
  status: null
});

const { columns, columnChecks, data, getData, getDataByPage, loading, mobilePagination } = useNaivePaginatedTable({
  api: () => roleApi.list(searchParams.value),
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
      key: 'name',
      title: $t('page.system.role.form.name'),
      align: 'center',
      width: 160
    },
    {
      key: 'code',
      title: $t('page.system.role.form.code'),
      align: 'center',
      width: 160
    },
    {
      key: 'data_scope',
      title: $t('page.system.role.form.dataScope'),
      align: 'center',
      width: 140,
      render: row => {
        if (!row.data_scope) {
          return null;
        }

        const tagMap: Record<DataScope, NaiveUI.ThemeColor> = {
          '1': 'default',
          '2': 'primary',
          '3': 'info',
          '4': 'warning',
          '5': 'success'
        };

        return <NTag type={tagMap[row.data_scope]}>{$t(dataScopeRecord[row.data_scope])}</NTag>;
      }
    },
    {
      key: 'status',
      title: $t('page.system.role.form.status'),
      align: 'center',
      width: 100,
      render: row => {
        if (!row.status) {
          return null;
        }

        const tagMap: Record<EnableStatus, NaiveUI.ThemeColor> = {
          '1': 'success',
          '0': 'warning'
        };

        return <NTag type={tagMap[row.status]}>{$t(enableStatusRecord[row.status])}</NTag>;
      }
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
      width: 300,
      fixed: 'right',
      render: row => (
        <div class="flex-center gap-8px">
          <NButton size="small" type="info" ghost onClick={() => handleOpenAssignMenus(row)}>
            {$t('page.system.role.action.assignMenus')}
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
  await roleApi.batchDelete(checkedRowKeys.value.map(Number));

  onBatchDeleted();
}

async function handleDelete(id: number) {
  await roleApi.remove(id);

  onDeleted();
}

function edit(id: number) {
  handleEdit(id);
}

const assignMenusVisible = ref(false);
const assignMenusRoleId = ref<number | null>(null);
const assignMenuIds = ref<number[]>([]);
const menuTreeOptions = ref<Api.System.Menu[]>([]);

async function getMenuTreeOptions() {
  const { error, data: menus } = await menuApi.tree();

  if (!error) {
    menuTreeOptions.value = menus ?? [];
  }
}

function handleOpenAssignMenus(row: Api.System.Role) {
  assignMenusRoleId.value = row.id;
  assignMenuIds.value = row.menus ?? [];
  assignMenusVisible.value = true;

  getMenuTreeOptions();
}

async function handleSubmitAssignMenus() {
  if (!assignMenusRoleId.value) {
    return;
  }

  const { error } = await roleApi.assignMenus(assignMenusRoleId.value, assignMenuIds.value);

  if (!error) {
    window.$message?.success($t('page.system.common.assignMenusSuccess'));

    assignMenusVisible.value = false;

    await getData();
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <RoleSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard :title="$t('page.system.role.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
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
        :scroll-x="1152"
        class="sm:h-full"
      />
      <RoleOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getDataByPage"
      />
    </NCard>
    <NModal
      v-model:show="assignMenusVisible"
      preset="card"
      :title="$t('page.system.role.action.assignMenus')"
      class="w-480px"
    >
      <NTreeSelect
        v-model:value="assignMenuIds"
        :options="menuTreeOptions"
        key-field="id"
        label-field="title"
        multiple
        checkable
        cascade
        clearable
      />
      <template #footer>
        <NSpace justify="end" :size="16">
          <NButton @click="assignMenusVisible = false">{{ $t('common.cancel') }}</NButton>
          <NButton type="primary" @click="handleSubmitAssignMenus">{{ $t('common.confirm') }}</NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>
