<script setup lang="tsx">
import { computed, ref } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import { $t } from '@/locales';
import { useAppStore } from '@/store/modules/app';
import { enableStatusOptions, enableStatusRecord } from '@/constants/business';
import type { EnableStatus } from '@/constants/business';
import { translateOptions } from '@/utils/common';
import { deptApi } from '@/service/api';
import DeptOperateModal from './modules/dept-operate-modal.vue';

const appStore = useAppStore();

/** search params */
const searchParams = ref<{ keyword: string; status: EnableStatus | '' }>({
  keyword: '',
  status: ''
});

const loading = ref(false);

const treeData = ref<Api.System.Department[]>([]);

async function getData() {
  loading.value = true;

  try {
    const { data: resData, error } = await deptApi.tree();

    if (!error) {
      treeData.value = resData || [];
    }
  } finally {
    loading.value = false;
  }
}

function filterTree(
  items: Api.System.Department[],
  keyword: string,
  status: EnableStatus | ''
): Api.System.Department[] {
  const result: Api.System.Department[] = [];

  for (const item of items) {
    const matchKeyword =
      !keyword || item.name?.includes(keyword) || item.code?.includes(keyword) || item.leader?.includes(keyword);
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
const editingData = ref<Api.System.Department | null>(null);

function handleAdd() {
  operateType.value = 'add';
  editingData.value = null;
  visible.value = true;
}

function handleEdit(row: Api.System.Department) {
  operateType.value = 'edit';
  editingData.value = row;
  visible.value = true;
}

function handleAddChildDept(id: number) {
  operateType.value = 'add';
  editingData.value = { id } as Api.System.Department;
  visible.value = true;
}

async function handleDelete(id: number) {
  const { error } = await deptApi.remove(id);

  if (!error) {
    window.$message?.success($t('common.deleteSuccess'));
    await getData();
  }
}

const columns = computed<NaiveUI.TableColumn<Api.System.Department>[]>(() => [
  {
    key: 'name',
    title: $t('page.system.dept.form.name'),
    align: 'center',
    width: 200
  },
  {
    key: 'code',
    title: $t('page.system.dept.form.code'),
    align: 'center',
    width: 160
  },
  {
    key: 'leader',
    title: $t('page.system.dept.form.leader'),
    align: 'center',
    width: 120
  },
  {
    key: 'phone',
    title: $t('page.system.dept.form.phone'),
    align: 'center',
    width: 140
  },
  {
    key: 'email',
    title: $t('page.system.dept.form.email'),
    align: 'center',
    width: 180
  },
  {
    key: 'status',
    title: $t('page.system.dept.form.status'),
    align: 'center',
    width: 100,
    render: row => {
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
    width: 230,
    fixed: 'right',
    render: row => (
      <div class="flex-center gap-8px">
        <NButton type="primary" ghost size="small" onClick={() => handleAddChildDept(row.id)}>
          {$t('common.addChildDept')}
        </NButton>
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
          <NFormItemGi span="24 s:12 m:6" :label="$t('page.system.dept.form.status')" class="pr-24px">
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
    <NCard :title="$t('page.system.dept.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
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
        class="sm:h-full"
      />
      <DeptOperateModal
        v-model:visible="visible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getData"
      />
    </NCard>
  </div>
</template>
