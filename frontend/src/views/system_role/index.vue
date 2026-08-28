<script setup lang="ts">
import { computed, h, reactive, ref, watch } from 'vue';
import { NTag, useMessage, useDialog, type FormInst, type FormRules } from 'naive-ui';
import type { FlatResponseData } from '@sa/axios';
import { $t } from '@/locales';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { roleApi, menuApi, deptApi } from '@/service/api';

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
  name: string;
  code: string;
  data_scope: '1' | '2' | '3' | '4' | '5';
  status: '1' | '0';
  menuIds: number[];
  departmentIds: number[];
  remark: string;
}>({
  name: '',
  code: '',
  data_scope: '1',
  status: '1',
  menuIds: [],
  departmentIds: [],
  remark: ''
});

const menuTree = ref<Api.System.Menu[]>([]);
const deptTree = ref<Api.System.Department[]>([]);

async function loadOptions() {
  const [menuRes, deptRes] = await Promise.all([menuApi.tree(), deptApi.tree()]);
  if (!menuRes.error) menuTree.value = menuRes.data || [];
  if (!deptRes.error) deptTree.value = deptRes.data || [];
}
loadOptions();

const drawerRules = computed<FormRules>(() => ({
  name: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  code: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  data_scope: [{ required: true, message: $t('form.required'), trigger: 'change' }],
  status: [{ required: true, message: $t('form.required'), trigger: 'change' }]
}));

const dataScopeOptions = computed(() => [
  { label: $t('page.system.common.dataScope.all'), value: '1' },
  { label: $t('page.system.common.dataScope.custom'), value: '2' },
  { label: $t('page.system.common.dataScope.dept'), value: '3' },
  { label: $t('page.system.common.dataScope.deptAndChildren'), value: '4' },
  { label: $t('page.system.common.dataScope.self'), value: '5' }
]);

type Row = Api.System.Role;
type Resp = FlatResponseData<App.Service.Response, Api.System.ListResp<Row>>;
type TableInst = ReturnType<typeof useNaivePaginatedTable<Resp, Row>>;

// 先声明为 undefined 再赋值：api 闭包首次同步调用时 tbl 尚未就绪，需可选链兜底（不能改 const，否则 TDZ）
let tbl: TableInst | undefined;
// eslint-disable-next-line prefer-const
tbl = useNaivePaginatedTable<Resp, Row>({
  api: () => {
    const params: Api.System.SearchParams = {
      current: tbl?.pagination?.page ?? 1,
      size: tbl?.pagination?.pageSize ?? 10,
      keyword: queryForm.keyword || undefined,
      status: queryForm.status || undefined
    };
    return roleApi.list(params);
  },
  columns: () => [
    { type: 'selection', width: 60 },
    {
      title: $t('common.index'),
      key: '__index__',
      width: 64,
      render: (_row, rowIndex) => ((tbl?.pagination?.page ?? 1) - 1) * (tbl?.pagination?.pageSize ?? 10) + rowIndex + 1
    },
    { title: 'ID', key: 'id', width: 80 },
    { title: $t('page.system.role.form.name'), key: 'name', width: 160 },
    { title: $t('page.system.role.form.code'), key: 'code', width: 160 },
    {
      title: $t('page.system.role.form.dataScope'),
      key: 'data_scope',
      width: 180,
      render: row => dataScopeOptions.value.find(o => o.value === row.data_scope)?.label || '-'
    },
    {
      title: $t('page.system.role.form.status'),
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
    { title: $t('page.system.role.form.remark'), key: 'remark', width: 200 },
    { title: $t('page.system.common.createdAt'), key: 'created_at', width: 180 },
    {
      title: $t('common.operate'),
      key: 'actions',
      width: 260,
      fixed: 'right',
      render: row =>
        h('div', { style: { display: 'flex', gap: '8px' } }, [
          createButtonAssignMenus(row),
          createButtonEdit(row),
          createButtonDelete(row)
        ])
    }
  ],
  transform: defaultTransform
});

const { data, loading, columns, columnChecks, getData, getDataByPage, mobilePagination } = tbl;
const {
  drawerVisible,
  closeDrawer,
  operateType,
  handleAdd,
  editingData,
  handleEdit,
  checkedRowKeys,
  onBatchDeleted,
  onDeleted
} = useTableOperate(data, 'id', getData);

watch(
  editingData,
  v => {
    if (v) {
      Object.assign(drawerForm, {
        name: v.name || '',
        code: v.code || '',
        data_scope: v.data_scope || '1',
        status: v.status || '1',
        menuIds: v.menuIds || v.menus || [],
        departmentIds: v.departmentIds || v.departments || [],
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
    name: '',
    code: '',
    data_scope: '1' as const,
    status: '1' as const,
    menuIds: [],
    departmentIds: [],
    remark: ''
  };
}

async function onSubmit() {
  const valid = await drawerFormRef.value?.validate().catch(() => false);
  if (!valid) {
    message.warning($t('common.pleaseCheckValue'));
    return;
  }
  const payload = { ...drawerForm };
  const { error } =
    operateType.value === 'add'
      ? await roleApi.add(payload)
      : await roleApi.update(editingData.value!.id, payload);
  if (error) return;
  message.success(operateType.value === 'add' ? $t('common.addSuccess') : $t('common.modifySuccess'));
  closeDrawer();
  await getData();
}

function createButtonEdit(row: Row) {
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

function createButtonDelete(row: Row) {
  return h(
    'NPopconfirm',
    {
      onPositiveClick: async () => {
        const { error } = await roleApi.remove(row.id);
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

function createButtonAssignMenus(row: Row) {
  return h(
    'NButton',
    {
      size: 'small',
      type: 'info',
      ghost: true,
      onClick: () => openAssignMenus(row)
    },
    { default: () => $t('page.system.role.action.assignMenus') }
  );
}

const assignMenusVisible = ref(false);
const assignMenusRoleId = ref<number | null>(null);
const assignMenusSelected = ref<number[]>([]);

function openAssignMenus(row: Row) {
  assignMenusRoleId.value = row.id;
  assignMenusSelected.value = row.menus || [];
  assignMenusVisible.value = true;
}

async function onAssignMenusSubmit() {
  if (!assignMenusRoleId.value) return;
  const { error } = await roleApi.assignMenus(assignMenusRoleId.value, assignMenusSelected.value);
  if (!error) {
    message.success($t('page.system.common.assignMenusSuccess'));
    assignMenusVisible.value = false;
    await getData();
  }
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
      const { error } = await roleApi.batchDelete(ids);
      if (!error) onBatchDeleted();
    }
  });
}

function onSearch() {
  getDataByPage();
}
function onReset() {
  Object.assign(queryForm, {
    keyword: '',
    status: ''
  });
  onSearch();
}
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
          <NFormItem :label="$t('page.system.role.form.status')">
            <NSelect
              v-model:value="queryForm.status"
              :options="[
                { label: $t('page.system.common.enabled'), value: '1' },
                { label: $t('page.system.common.disabled'), value: '0' }
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
          v-model:checked-row-keys="checkedRowKeys"
          :columns="columns"
          :data="data"
          :loading="loading"
          :pagination="mobilePagination"
          :scroll-x="1500"
          :bordered="false"
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
          <NFormItem :label="$t('page.system.role.form.name')" path="name">
            <NInput v-model:value="drawerForm.name" />
          </NFormItem>
          <NFormItem :label="$t('page.system.role.form.code')" path="code">
            <NInput v-model:value="drawerForm.code" />
          </NFormItem>
          <NFormItem :label="$t('page.system.role.form.dataScope')" path="data_scope">
            <NSelect v-model:value="drawerForm.data_scope" :options="dataScopeOptions" />
          </NFormItem>
          <NFormItem :label="$t('page.system.role.form.status')" path="status">
            <NRadioGroup v-model:value="drawerForm.status">
              <NRadio value="1">{{ $t('page.system.common.enabled') }}</NRadio>
              <NRadio value="0">{{ $t('page.system.common.disabled') }}</NRadio>
            </NRadioGroup>
          </NFormItem>
          <NFormItem :label="$t('page.system.role.form.menus')" path="menuIds">
            <NTreeSelect
              v-model:value="drawerForm.menuIds"
              :options="menuTree"
              key-field="id"
              label-field="title"
              children-field="children"
              multiple
              cascade
              clearable
            />
          </NFormItem>
          <NFormItem
            v-if="drawerForm.data_scope === '2'"
            :label="$t('page.system.role.form.departments')"
            path="departmentIds"
          >
            <NTreeSelect
              v-model:value="drawerForm.departmentIds"
              :options="deptTree"
              key-field="id"
              label-field="name"
              children-field="children"
              multiple
              cascade
              clearable
            />
          </NFormItem>
          <NFormItem :label="$t('page.system.role.form.remark')" path="remark">
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

    <NModal v-model:show="assignMenusVisible" preset="card" :title="$t('page.system.role.action.assignMenus')" style="width: 600px">
      <NTreeSelect
        v-model:value="assignMenusSelected"
        :options="menuTree"
        key-field="id"
        label-field="title"
        children-field="children"
        multiple
        cascade
        clearable
      />
      <template #footer>
        <NSpace justify="end">
          <NButton @click="assignMenusVisible = false">{{ $t('common.cancel') }}</NButton>
          <NButton type="primary" :loading="loading" @click="onAssignMenusSubmit">
            {{
              $t('common.confirm')
            }}
          </NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>
