<script setup lang="ts">
import { computed, h, reactive, ref, watch } from 'vue';
import { useMessage, useDialog, type FormInst, type FormRules } from 'naive-ui';
import { $t } from '@/locales';
import { useTableOperate } from '@/hooks/common/table';
import { menuApi } from '@/service/api';

const message = useMessage();
const dialog = useDialog();

const formRef = ref<FormInst | null>(null);
const queryForm = reactive<{
  keyword: string;
  status: '' | '1' | '0';
}>({
  keyword: '',
  status: ''
});

const drawerFormRef = ref<FormInst | null>(null);
const drawerForm = reactive<{
  parentId: number | null;
  name: string;
  title: string;
  path: string;
  component: string;
  permission: string;
  icon: string;
  menu_type: '1' | '2' | '3';
  order: number;
  i18n_key: string;
  keep_alive: boolean;
  hide_in_menu: boolean;
  external_link: string;
  status: '1' | '0';
  remark: string;
}>({
  parentId: null,
  name: '',
  title: '',
  path: '',
  component: '',
  permission: '',
  icon: '',
  menu_type: '1',
  order: 0,
  i18n_key: '',
  keep_alive: false,
  hide_in_menu: false,
  external_link: '',
  status: '1',
  remark: ''
});

const menuTree = ref<any[]>([]);

async function loadMenuTree() {
  const { data: resData, error } = await menuApi.tree();
  if (!error) {
    menuTree.value = resData || [];
  }
}

const drawerRules = computed<FormRules>(() => ({
  name: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  title: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  menu_type: [{ required: true, message: $t('form.required'), trigger: 'change' }],
  status: [{ required: true, message: $t('form.required'), trigger: 'change' }]
}));

const menuTypeOptions = [
  { label: '目录', value: '1' },
  { label: '菜单', value: '2' },
  { label: '按钮', value: '3' }
];

function filterTree(
  items: any[],
  keyword: string,
  status: '' | '1' | '0'
): any[] {
  const result: any[] = [];
  for (const item of items) {
    const matchKeyword =
      !keyword ||
      item.title?.includes(keyword) ||
      item.name?.includes(keyword) ||
      item.path?.includes(keyword);
    const matchStatus = !status || item.status === status;
    const filteredChildren = item.children
      ? filterTree(item.children, keyword, status)
      : [];
    if ((matchKeyword && matchStatus) || filteredChildren.length > 0) {
      result.push({
        ...item,
        children: filteredChildren.length > 0 ? filteredChildren : item.children
      });
    }
  }
  return result;
}

const loading = ref<boolean>(false);
const rawData = ref<any[]>([]);

const data = computed(() => filterTree(rawData.value, queryForm.keyword, queryForm.status));

async function getData() {
  loading.value = true;
  try {
    const { data: resData, error } = await menuApi.tree();
    if (!error) {
      menuTree.value = resData || [];
      rawData.value = resData || [];
    }
  } finally {
    loading.value = false;
  }
}

const columns = computed<any[]>(() => [
  {
    title: $t('page.system.menu.form.title'),
    key: 'title',
    width: 200
  },
  { title: $t('page.system.menu.form.path'), key: 'path', width: 200 },
  { title: $t('page.system.menu.form.component'), key: 'component', width: 200 },
  {
    title: $t('page.system.menu.form.type'),
    key: 'menu_type',
    width: 100,
    render: (row: any) => menuTypeOptions.find(o => o.value === row.menu_type)?.label || '-'
  },
  { title: $t('page.system.menu.form.icon'), key: 'icon', width: 100 },
  { title: $t('page.system.menu.form.order'), key: 'order', width: 80 },
  {
    title: $t('page.system.menu.form.status'),
    key: 'status',
    width: 100,
    render: (row: any) =>
      h(
        'span',
        {
          style: {
            color: row.status === '1' ? '#18a058' : '#d03050'
          }
        },
        row.status === '1' ? '正常' : '停用'
      )
  },
  {
    title: $t('common.operate'),
    key: 'actions',
    width: 200,
    fixed: 'right',
    render: (row: any): any =>
      h('div', { style: { display: 'flex', gap: '8px' } }, [
        createButtonEdit(row),
        createButtonDelete(row)
      ])
  }
]);

const columnChecks = ref<NaiveUI.TableColumnCheck[]>([]);

const ops: any = (useTableOperate as any)(data as any, 'id', getData);
const drawerVisible = ops.drawerVisible;
const openDrawer = ops.openDrawer;
const closeDrawer = ops.closeDrawer;
const operateType = ops.operateType;
const handleAdd = ops.handleAdd;
const editingData = ops.editingData;
const handleEdit = ops.handleEdit;
const checkedRowKeys = ops.checkedRowKeys;
const onBatchDeleted = ops.onBatchDeleted;
const onDeleted = ops.onDeleted;

watch(
  editingData,
  (v: any) => {
    if (v) {
      Object.assign(drawerForm, {
        parentId: v.parentId || null,
        name: v.name || '',
        title: v.title || '',
        path: v.path || '',
        component: v.component || '',
        permission: v.permission || '',
        icon: v.icon || '',
        menu_type: v.menu_type || '1',
        order: v.order || 0,
        i18n_key: v.i18n_key || '',
        keep_alive: v.keep_alive || false,
        hide_in_menu: v.hide_in_menu || false,
        external_link: v.external_link || '',
        status: v.status || '1',
        remark: v.remark || ''
      });
    } else {
      Object.assign(drawerForm, defaultForm());
    }
  },
  { immediate: true }
);

function defaultForm() {
  return {
    parentId: null as number | null,
    name: '',
    title: '',
    path: '',
    component: '',
    permission: '',
    icon: '',
    menu_type: '1' as const,
    order: 0,
    i18n_key: '',
    keep_alive: false,
    hide_in_menu: false,
    external_link: '',
    status: '1' as const,
    remark: ''
  };
}

async function onSubmit() {
  const valid = await drawerFormRef.value?.validate().catch(() => false);
  if (!valid) {
    message.warning($t('common.pleaseCheckValue'));
    return;
  }
  const payload: any = { ...drawerForm };
  const { error } =
    operateType.value === 'add'
      ? await menuApi.add(payload)
      : await menuApi.update(editingData.value!.id, payload);
  if (error) return;
  message.success(operateType.value === 'add' ? $t('common.addSuccess') : $t('common.modifySuccess'));
  closeDrawer();
  await getData();
}

function createButtonEdit(row: any): any {
  return h(
    'NButton',
    {
      size: 'small',
      type: 'primary',
      ghost: true,
      onClick: () => handleEdit(row.id)
    },
    { default: () => $t('common.edit') }
  );
}

function createButtonDelete(row: any): any {
  return h(
    'NPopconfirm',
    {
      onPositiveClick: async () => {
        const { error } = await menuApi.remove(row.id);
        if (!error) onDeleted();
      }
    },
    {
      trigger: () =>
        h(
          'NButton',
          {
            size: 'small',
            type: 'error',
            ghost: true
          },
          { default: () => $t('common.delete') }
        ),
      default: () => $t('common.confirmDelete')
    }
  );
}

async function onBatchDelete() {
  if (!checkedRowKeys.value.length) return;
  dialog.warning({
    title: $t('common.warning'),
    content: $t('common.confirmDelete'),
    positiveText: $t('common.confirm'),
    negativeText: $t('common.cancel'),
    onPositiveClick: async () => {
      const ids = checkedRowKeys.value.map(Number);
      const { error } = await menuApi.batchDelete(ids);
      if (!error) onBatchDeleted();
    }
  });
}

function onSearch() {
  getData();
}
function onReset() {
  Object.assign(queryForm, {
    keyword: '',
    status: ''
  });
  onSearch();
}

getData();
loadMenuTree();
</script>

<template>
  <NSpace vertical :size="12">
    <NCard>
      <NForm ref="formRef" inline label-placement="left" label-width="auto" :model="queryForm">
        <NFormItem :label="$t('common.keywordSearch')">
          <NInput
            v-model:value="queryForm.keyword"
            clearable
            :placeholder="$t('common.keywordSearch')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.status')">
          <NSelect
            v-model:value="queryForm.status"
            :options="[
              { label: '正常', value: '1' },
              { label: '停用', value: '0' }
            ]"
            clearable
          />
        </NFormItem>
        <NFormItem>
          <NSpace>
            <NButton type="primary" @click="onSearch">
              <template #icon><icon-mdi-magnify class="text-icon" /></template>{{ $t('common.search') }}
            </NButton>
            <NButton @click="onReset">
              <template #icon><icon-mdi-refresh class="text-icon" /></template>{{ $t('common.reset') }}
            </NButton>
          </NSpace>
        </NFormItem>
      </NForm>
    </NCard>

    <NCard :bordered="false" class="!mt-0">
      <TableHeaderOperation
        v-model:columns="columnChecks"
        :loading="loading"
        :disabled-delete="!checkedRowKeys.length"
        @add="handleAdd"
        @delete="onBatchDelete"
        @refresh="getData"
      />

      <NDataTable
        :columns="columns"
        :data="data"
        :loading="loading"
        :pagination="false"
        v-model:checked-row-keys="checkedRowKeys"
        :scroll-x="1400"
        :bordered="false"
        :children-key="'children'"
        :remote="false"
        striped
      />
    </NCard>
  </NSpace>

  <NDrawer v-model:show="drawerVisible" :width="640" placement="right" :mask-closable="false">
    <NDrawerContent
      :title="operateType === 'add' ? $t('common.add') : $t('common.edit')"
      :closable="true"
    >
      <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
        <NButton size="small" @click="closeDrawer">{{ $t('common.close') }}</NButton>
      </div>
      <NForm ref="drawerFormRef" label-placement="top" :model="drawerForm" :rules="drawerRules">
        <NFormItem :label="$t('page.system.menu.form.parent')" path="parentId">
          <NTreeSelect
            v-model:value="drawerForm.parentId"
            :options="menuTree"
            key-field="id"
            label-field="title"
            children-field="children"
            clearable
          />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.name')" path="name">
          <NInput v-model:value="drawerForm.name" />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.title')" path="title">
          <NInput v-model:value="drawerForm.title" />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.path')" path="path">
          <NInput v-model:value="drawerForm.path" />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.component')" path="component">
          <NInput v-model:value="drawerForm.component" />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.permission')" path="permission">
          <NInput v-model:value="drawerForm.permission" />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.icon')" path="icon">
          <NInput v-model:value="drawerForm.icon" />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.type')" path="menu_type">
          <NRadioGroup v-model:value="drawerForm.menu_type">
            <NRadio value="1">目录</NRadio>
            <NRadio value="2">菜单</NRadio>
            <NRadio value="3">按钮</NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.order')" path="order">
          <NInputNumber v-model:value="drawerForm.order" :min="0" />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.i18nKey')" path="i18n_key">
          <NInput v-model:value="drawerForm.i18n_key" />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.keepAlive')" path="keep_alive">
          <NSwitch v-model:value="drawerForm.keep_alive" />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.hideInMenu')" path="hide_in_menu">
          <NSwitch v-model:value="drawerForm.hide_in_menu" />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.externalLink')" path="external_link">
          <NInput v-model:value="drawerForm.external_link" />
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.status')" path="status">
          <NRadioGroup v-model:value="drawerForm.status">
            <NRadio value="1">正常</NRadio>
            <NRadio value="0">停用</NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.menu.form.remark')" path="remark">
          <NInput v-model:value="drawerForm.remark" type="textarea" :rows="3" />
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace justify="end">
          <NButton @click="closeDrawer">{{ $t('common.cancel') }}</NButton>
          <NButton type="primary" :loading="loading" @click="onSubmit">{{ $t('common.confirm') }}</NButton>
        </NSpace>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>
