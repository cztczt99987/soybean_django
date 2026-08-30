<script setup lang="tsx">
import { ref, watch } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import type { TreeInst, TreeOption } from 'naive-ui';
import type { DataScope, EnableStatus } from '@/constants/business';
import { dataScopeOptions, dataScopeRecord, enableStatusRecord } from '@/constants/business';
import { menuApi, roleApi } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { translateOptions } from '@/utils/common';
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
const assignMenusRoleName = ref('');
/** 数据授权 */
const assignDataScope = ref<DataScope>('1');
/** 勾选的菜单 id（含半选父目录，提交前合并） */
const assignMenuIds = ref<number[]>([]);
const assignMenuPattern = ref('');
/** 父子联动（开启后勾选自动级联父子节点） */
const assignCascade = ref(true);
const menuTreeOptions = ref<Api.System.Menu[]>([]);
/** 可展开的父节点 key（用于展开/收起切换） */
const expandableKeys = ref<number[]>([]);
const assignExpandedKeys = ref<number[]>([]);
const assignTreeRef = ref<TreeInst | null>(null);

const menuTypeColorMap: Record<string, NaiveUI.ThemeColor> = {
  '1': 'warning',
  '2': 'info',
  '3': 'default'
};

const menuTypeLocaleMap: Record<string, App.I18n.I18nKey> = {
  '1': 'page.system.common.menuType.dir',
  '2': 'page.system.common.menuType.menu',
  '3': 'page.system.common.menuType.button'
};

function renderMenuLabel({ option }: { option: TreeOption }) {
  const menu = option as unknown as Api.System.Menu;

  return (
    <span class="inline-flex items-center gap-6px">
      <span>{menu.title}</span>
      <NTag size="tiny" type={menuTypeColorMap[menu.menu_type]} bordered={false}>
        {$t(menuTypeLocaleMap[menu.menu_type])}
      </NTag>
    </span>
  );
}

function collectExpandableKeys(menus: Api.System.Menu[], keys: number[] = []) {
  menus.forEach(menu => {
    if (menu.children?.length) {
      keys.push(menu.id);
      collectExpandableKeys(menu.children, keys);
    }
  });
  return keys;
}

async function getMenuTreeOptions() {
  const { error, data: menus } = await menuApi.tree();

  if (!error) {
    menuTreeOptions.value = menus ?? [];
    expandableKeys.value = collectExpandableKeys(menuTreeOptions.value);
    assignExpandedKeys.value = [...expandableKeys.value];
  }
}

function handleOpenAssignMenus(row: Api.System.Role) {
  assignMenusRoleId.value = row.id;
  assignMenusRoleName.value = row.name;
  assignDataScope.value = row.data_scope ?? '1';
  assignMenuIds.value = row.menus ?? [];
  assignMenuPattern.value = '';
  assignCascade.value = true;
  assignMenusVisible.value = true;

  getMenuTreeOptions();
}

/** 搜索时自动展开全部节点，保证能搜到深层菜单 */
watch(assignMenuPattern, pattern => {
  if (pattern) {
    assignExpandedKeys.value = [...expandableKeys.value];
  }
});

function handleToggleExpand() {
  assignExpandedKeys.value = assignExpandedKeys.value.length ? [] : [...expandableKeys.value];
}

function handleExpandedKeysChange(keys: Array<string | number>) {
  assignExpandedKeys.value = keys.map(Number);
}

function handleAssignCheckedKeys(keys: Array<string | number>) {
  assignMenuIds.value = keys.map(Number);
}

async function handleSubmitAssignMenus() {
  if (!assignMenusRoleId.value) {
    return;
  }

  // 联动时合并半选父目录，保证菜单树父子链完整；非联动时直接使用勾选值
  const checked = (assignTreeRef.value?.getCheckedData().keys ?? []) as Array<string | number>;
  const indeterminate = assignCascade.value
    ? ((assignTreeRef.value?.getIndeterminateData().keys ?? []) as Array<string | number>)
    : [];
  const menuIds = [...new Set([...checked, ...indeterminate])].map(Number);

  const { error } = await roleApi.assignMenus(assignMenusRoleId.value, menuIds, assignDataScope.value);

  if (!error) {
    window.$message?.success($t('page.system.common.assignPermissionSuccess'));

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
    <NDrawer v-model:show="assignMenusVisible" :width="820" placement="right">
      <NDrawerContent
        :title="`【${assignMenusRoleName}】${$t('page.system.role.action.assignPermission')}`"
        closable
      >
        <div class="flex gap-32px lt-sm:flex-col">
          <!-- 数据授权 -->
          <div class="w-280px flex-shrink-0">
            <div class="mb-12px flex items-center gap-8px">
              <span class="h-16px w-4px rounded-full bg-primary" />
              <span class="font-medium">{{ $t('page.system.role.assign.dataAuth') }}</span>
              <NTooltip>
                <template #trigger>
                  <icon-ic-round-help-outline class="text-icon" />
                </template>
                {{ $t('page.system.role.assign.dataAuthTip') }}
              </NTooltip>
            </div>
            <NSelect v-model:value="assignDataScope" :options="translateOptions(dataScopeOptions)" />
          </div>
          <!-- 菜单授权 -->
          <div class="min-w-0 flex-1">
            <div class="mb-12px flex items-center gap-8px">
              <span class="h-16px w-4px rounded-full bg-primary" />
              <span class="font-medium">{{ $t('page.system.role.assign.menuAuth') }}</span>
              <NTooltip>
                <template #trigger>
                  <icon-ic-round-help-outline class="text-icon" />
                </template>
                {{ $t('page.system.role.assign.menuAuthTip') }}
              </NTooltip>
            </div>
            <div class="mb-12px flex items-center gap-12px">
              <NInput
                v-model:value="assignMenuPattern"
                clearable
                class="flex-1"
                :placeholder="$t('page.system.role.assign.searchMenu')"
              >
                <template #prefix>
                  <icon-ic-round-search class="text-icon" />
                </template>
              </NInput>
              <NButton secondary @click="handleToggleExpand">
                <template #icon>
                  <icon-ic-round-unfold-more v-if="assignExpandedKeys.length" />
                  <icon-ic-round-unfold-less v-else />
                </template>
                {{
                  assignExpandedKeys.length
                    ? $t('page.system.role.assign.collapse')
                    : $t('page.system.role.assign.expand')
                }}
              </NButton>
              <NCheckbox v-model:checked="assignCascade">
                {{ $t('page.system.role.assign.parentLinkage') }}
              </NCheckbox>
            </div>
            <div class="h-520px overflow-auto border border-gray-200 rounded-4px p-8px dark:border-gray-700">
              <NTree
                ref="assignTreeRef"
                :data="menuTreeOptions"
                key-field="id"
                label-field="title"
                children-field="children"
                checkable
                block-line
                :cascade="assignCascade"
                :check-strictly="!assignCascade"
                :expanded-keys="assignExpandedKeys"
                :pattern="assignMenuPattern"
                :checked-keys="assignMenuIds"
                :render-label="renderMenuLabel"
                @update:checked-keys="handleAssignCheckedKeys"
                @update:expanded-keys="handleExpandedKeysChange"
              />
            </div>
          </div>
        </div>
        <template #footer>
          <NSpace justify="end" :size="16">
            <NButton @click="assignMenusVisible = false">{{ $t('common.cancel') }}</NButton>
            <NButton type="primary" @click="handleSubmitAssignMenus">{{ $t('common.confirm') }}</NButton>
          </NSpace>
        </template>
      </NDrawerContent>
    </NDrawer>
  </div>
</template>
