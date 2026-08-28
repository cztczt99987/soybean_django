<script setup lang="ts">
import { computed, h, reactive, ref, watch } from 'vue';
import { NTag, useDialog, useMessage, type FormInst, type FormRules } from 'naive-ui';
import { $t } from '@/locales';
import { useTableOperate } from '@/hooks/common/table';
import { deptApi } from '@/service/api';

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
  code: string;
  leader: string;
  phone: string;
  email: string;
  status: '1' | '0';
  remark: string;
}>({
  parentId: null,
  name: '',
  code: '',
  leader: '',
  phone: '',
  email: '',
  status: '1',
  remark: ''
});

const deptTree = ref<Api.System.Department[]>([]);

async function loadDeptTree() {
  const { data: resData, error } = await deptApi.tree();
  if (!error) {
    deptTree.value = resData || [];
  }
}

const drawerRules = computed<FormRules>(() => ({
  name: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  code: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  status: [{ required: true, message: $t('form.required'), trigger: 'change' }]
}));

const statusOptions = computed(() => [
  { label: $t('page.system.common.enabled'), value: '1' },
  { label: $t('page.system.common.disabled'), value: '0' }
]);

function filterTree(items: Api.System.Department[], keyword: string, status: '' | '1' | '0'): Api.System.Department[] {
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

const loading = ref<boolean>(false);
const rawData = ref<Api.System.Department[]>([]);

const data = computed(() => filterTree(rawData.value, queryForm.keyword, queryForm.status));

async function getData() {
  loading.value = true;
  try {
    const { data: resData, error } = await deptApi.tree();
    if (!error) {
      deptTree.value = resData || [];
      rawData.value = resData || [];
    }
  } finally {
    loading.value = false;
  }
}

const columns = computed<NaiveUI.TableColumn<Api.System.Department>[]>(() => [
  {
    title: $t('page.system.dept.form.name'),
    key: 'name',
    width: 200
  },
  { title: $t('page.system.dept.form.code'), key: 'code', width: 160 },
  { title: $t('page.system.dept.form.leader'), key: 'leader', width: 120 },
  { title: $t('page.system.dept.form.phone'), key: 'phone', width: 140 },
  { title: $t('page.system.dept.form.email'), key: 'email', width: 180 },
  {
    title: $t('page.system.dept.form.status'),
    key: 'status',
    width: 100,
    render: row =>
      h(
        NTag,
        { size: 'small', type: row.status === '1' ? 'success' : 'error' },
        {
          default: () => (row.status === '1' ? $t('page.system.common.enabled') : $t('page.system.common.disabled'))
        }
      )
  },
  {
    title: $t('common.operate'),
    key: 'actions',
    width: 200,
    fixed: 'right',
    render: row =>
      h('div', { style: { display: 'flex', gap: '8px' } }, [createButtonEdit(row), createButtonDelete(row)])
  }
]);

const columnChecks = ref<NaiveUI.TableColumnCheck[]>([]);

const { drawerVisible, closeDrawer, operateType, handleAdd, editingData, handleEdit, checkedRowKeys, onBatchDeleted, onDeleted } =
  useTableOperate(data, 'id', getData);

watch(
  editingData,
  v => {
    if (v) {
      Object.assign(drawerForm, {
        parentId: v.parentId || null,
        name: v.name || '',
        code: v.code || '',
        leader: v.leader || '',
        phone: v.phone || '',
        email: v.email || '',
        status: v.status || '1',
        remark: v.remark || ''
      });
    } else {
      Object.assign(drawerForm, defaultForm());
    }
  },
  { immediate: true }
);

function defaultForm(): typeof drawerForm {
  return {
    parentId: null,
    name: '',
    code: '',
    leader: '',
    phone: '',
    email: '',
    status: '1',
    remark: ''
  };
}

async function onSubmit() {
  const valid = await drawerFormRef.value?.validate().catch(() => false);
  if (!valid) {
    message.warning($t('common.pleaseCheckValue'));
    return;
  }
  const payload: Partial<Api.System.Department> = { ...drawerForm };
  const { error } =
    operateType.value === 'add'
      ? await deptApi.add(payload)
      : await deptApi.update(editingData.value!.id, payload);
  if (error) return;
  message.success(operateType.value === 'add' ? $t('common.addSuccess') : $t('common.modifySuccess'));
  closeDrawer();
  await getData();
}

function createButtonEdit(row: Api.System.Department) {
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

function createButtonDelete(row: Api.System.Department) {
  return h(
    'NPopconfirm',
    {
      onPositiveClick: async () => {
        const { error } = await deptApi.remove(row.id);
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
      const { error } = await deptApi.batchDelete(ids);
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
loadDeptTree();
</script>

<template>
  <div class="min-h-full">
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
          <NFormItem :label="$t('page.system.dept.form.status')">
            <NSelect
              v-model:value="queryForm.status"
              :options="statusOptions"
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
          v-model:checked-row-keys="checkedRowKeys"
          :columns="columns"
          :data="data"
          :loading="loading"
          :pagination="false"
          :scroll-x="1300"
          :bordered="false"
          children-key="children"
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
          <NFormItem :label="$t('page.system.dept.form.parent')" path="parentId">
            <NTreeSelect
              v-model:value="drawerForm.parentId"
              :options="deptTree"
              key-field="id"
              label-field="name"
              children-field="children"
              clearable
            />
          </NFormItem>
          <NFormItem :label="$t('page.system.dept.form.name')" path="name">
            <NInput v-model:value="drawerForm.name" />
          </NFormItem>
          <NFormItem :label="$t('page.system.dept.form.code')" path="code">
            <NInput v-model:value="drawerForm.code" />
          </NFormItem>
          <NFormItem :label="$t('page.system.dept.form.leader')" path="leader">
            <NInput v-model:value="drawerForm.leader" />
          </NFormItem>
          <NFormItem :label="$t('page.system.dept.form.phone')" path="phone">
            <NInput v-model:value="drawerForm.phone" />
          </NFormItem>
          <NFormItem :label="$t('page.system.dept.form.email')" path="email">
            <NInput v-model:value="drawerForm.email" />
          </NFormItem>
          <NFormItem :label="$t('page.system.dept.form.status')" path="status">
            <NRadioGroup v-model:value="drawerForm.status">
              <NRadio value="1">{{ $t('page.system.common.enabled') }}</NRadio>
              <NRadio value="0">{{ $t('page.system.common.disabled') }}</NRadio>
            </NRadioGroup>
          </NFormItem>
          <NFormItem :label="$t('page.system.dept.form.remark')" path="remark">
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
  </div>
</template>
