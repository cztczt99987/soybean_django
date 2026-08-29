<script setup lang="tsx">
import { computed, ref } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import type { DataTableRowKey } from 'naive-ui';
import { $t } from '@/locales';
import { useAppStore } from '@/store/modules/app';
import SvgIcon from '@/components/custom/svg-icon.vue';
import { enableStatusOptions, enableStatusRecord, menuTypeRecord } from '@/constants/business';
import type { EnableStatus, MenuType } from '@/constants/business';
import { yesOrNoRecord } from '@/constants/common';
import { translateOptions } from '@/utils/common';
import { menuApi } from '@/service/api';
import MenuOperateModal from './modules/menu-operate-modal.vue';

const appStore = useAppStore();

/** search params */
const searchParams = ref<{ keyword: string; status: EnableStatus | '' }>({
  keyword: '',
  status: ''
});

const loading = ref(false);

const treeData = ref<Api.System.Menu[]>([]);

/** 展开的行 key，加载后默认展开全部层级以体现上下级 */
const expandedRowKeys = ref<DataTableRowKey[]>([]);

function collectAllRowKeys(items: Api.System.Menu[]): DataTableRowKey[] {
  return items.flatMap(item => [item.id, ...collectAllRowKeys(item.children || [])]);
}

async function getData() {
  loading.value = true;

  try {
    const { data: resData, error } = await menuApi.tree();

    if (!error) {
      treeData.value = resData || [];
      expandedRowKeys.value = collectAllRowKeys(treeData.value);
    }
  } finally {
    loading.value = false;
  }
}

function handleExpandedRowKeysUpdate(keys: DataTableRowKey[]) {
  expandedRowKeys.value = keys;
}

function filterTree(items: Api.System.Menu[], keyword: string, status: EnableStatus | ''): Api.System.Menu[] {
  const result: Api.System.Menu[] = [];

  for (const item of items) {
    const matchKeyword =
      !keyword || item.title?.includes(keyword) || item.name?.includes(keyword) || item.path?.includes(keyword);
    const matchStatus = !status || item.status === status;
    const filteredChildren = item.children ? filterTree(item.children, keyword, status) : [];

    if ((matchKeyword && matchStatus) || filteredChildren.length > 0) {
      result.push({
        ...item,
        children: filteredChildren.length > 0 ? filteredChildren : item.children
      });
    }
  }

  return result;
}

const filteredTree = computed(() => filterTree(treeData.value, searchParams.value.keyword, searchParams.value.status));

function handleSearch() {
  getData();
}

function handleReset() {
  Object.assign(searchParams.value, { keyword: '', status: '' });
  getData();
}

/** modal visible */
const visible = ref(false);

/** operate type */
const operateType = ref<NaiveUI.TableOperateType>('add');

/** the editing row data */
const editingData = ref<Api.System.Menu | null>(null);

function handleAdd() {
  operateType.value = 'add';
  editingData.value = null;
  visible.value = true;
}

function handleEdit(row: Api.System.Menu) {
  operateType.value = 'edit';
  editingData.value = row;
  visible.value = true;
}

function handleAddChildMenu(id: number) {
  operateType.value = 'add';
  editingData.value = { id } as Api.System.Menu;
  visible.value = true;
}

async function handleDelete(id: number) {
  const { error } = await menuApi.remove(id);

  if (!error) {
    window.$message?.success($t('common.deleteSuccess'));
    await getData();
  }
}

const columns = computed<NaiveUI.TableColumn<Api.System.Menu>[]>(() => [
  {
    key: 'name',
    title: $t('page.system.menu.form.name'),
    align: 'left',
    width: 220
  },
  {
    key: 'title',
    title: $t('page.system.menu.form.title'),
    align: 'center',
    width: 160
  },
  {
    key: 'icon',
    title: $t('page.system.menu.form.icon'),
    align: 'center',
    width: 60,
    render: row => <SvgIcon icon={row.icon} />
  },
  {
    key: 'path',
    title: $t('page.system.menu.form.path'),
    align: 'center',
    width: 160
  },
  {
    key: 'component',
    title: $t('page.system.menu.form.component'),
    align: 'center',
    width: 180
  },
  {
    key: 'menu_type',
    title: $t('page.system.menu.form.type'),
    align: 'center',
    width: 100,
    render: row => {
      const tagMap: Record<MenuType, NaiveUI.ThemeColor> = {
        '1': 'default',
        '2': 'primary',
        '3': 'warning'
      };

      return <NTag type={tagMap[row.menu_type]}>{$t(menuTypeRecord[row.menu_type])}</NTag>;
    }
  },
  {
    key: 'permission',
    title: $t('page.system.menu.form.permission'),
    align: 'center',
    width: 160
  },
  {
    key: 'order',
    title: $t('page.system.menu.form.order'),
    align: 'center',
    width: 80
  },
  {
    key: 'keep_alive',
    title: $t('page.system.menu.form.keepAlive'),
    align: 'center',
    width: 100,
    render: row => (
      <NTag type={row.keep_alive ? 'success' : 'default'}>
        {row.keep_alive ? $t('common.yesOrNo.yes') : $t('common.yesOrNo.no')}
      </NTag>
    )
  },
  {
    key: 'hide_in_menu',
    title: $t('page.system.menu.form.hideInMenu'),
    align: 'center',
    width: 110,
    render: row => {
      const tagMap: Record<CommonType.YesOrNo, NaiveUI.ThemeColor> = {
        Y: 'error',
        N: 'default'
      };

      const key: CommonType.YesOrNo = row.hide_in_menu ? 'Y' : 'N';

      return <NTag type={tagMap[key]}>{$t(yesOrNoRecord[key])}</NTag>;
    }
  },
  {
    key: 'status',
    title: $t('page.system.menu.form.status'),
    align: 'center',
    width: 90,
    render: row => {
      const tagMap: Record<EnableStatus, NaiveUI.ThemeColor> = {
        '1': 'success',
        '0': 'warning'
      };

      return <NTag type={tagMap[row.status]}>{$t(enableStatusRecord[row.status])}</NTag>;
    }
  },
  {
    key: 'operate',
    title: $t('common.operate'),
    align: 'center',
    width: 230,
    fixed: 'right',
    render: row => (
      <div class="flex-center gap-8px">
        {row.menu_type === '1' || row.menu_type === '2' ? (
          <NButton type="primary" ghost size="small" onClick={() => handleAddChildMenu(row.id)}>
            {$t('common.addChildMenu')}
          </NButton>
        ) : null}
        <NButton type="primary" ghost size="small" onClick={() => handleEdit(row)}>
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
]);

getData();
</script>

<template>
  <div class="flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NCard :bordered="false" size="small" class="card-wrapper">
      <NForm label-placement="left" :label-width="80">
        <NGrid responsive="screen" item-responsive>
          <NFormItemGi span="24 s:12 m:6" :label="$t('common.keywordSearch')" class="pr-24px">
            <NInput v-model:value="searchParams.keyword" :placeholder="$t('common.keywordSearch')" clearable />
          </NFormItemGi>
          <NFormItemGi span="24 s:12 m:6" :label="$t('page.system.menu.form.status')" class="pr-24px">
            <NSelect
              v-model:value="searchParams.status"
              :options="translateOptions(enableStatusOptions)"
              clearable
            />
          </NFormItemGi>
          <NFormItemGi span="24 s:12 m:6">
            <NSpace class="w-full" justify="end">
              <NButton @click="handleReset">
                <template #icon>
                  <icon-ic-round-refresh class="text-icon" />
                </template>
                {{ $t('common.reset') }}
              </NButton>
              <NButton type="primary" ghost @click="handleSearch">
                <template #icon>
                  <icon-ic-round-search class="text-icon" />
                </template>
                {{ $t('common.search') }}
              </NButton>
            </NSpace>
          </NFormItemGi>
        </NGrid>
      </NForm>
    </NCard>
    <NCard :title="$t('page.system.menu.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <TableHeaderOperation :loading="loading" @refresh="getData">
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
        :data="filteredTree"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="1088"
        :loading="loading"
        :row-key="row => row.id"
        children-key="children"
        :expanded-row-keys="expandedRowKeys"
        @update:expanded-row-keys="handleExpandedRowKeysUpdate"
        class="sm:h-full"
      />
      <MenuOperateModal
        v-model:visible="visible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getData"
      />
    </NCard>
  </div>
</template>
