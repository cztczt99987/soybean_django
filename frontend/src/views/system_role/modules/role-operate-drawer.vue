<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { dataScopeOptions, enableStatusOptions } from '@/constants/business';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { deptApi, menuApi, roleApi } from '@/service/api';
import { translateOptions } from '@/utils/common';
import { $t } from '@/locales';

defineOptions({ name: 'RoleOperateDrawer' });

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.System.Role | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', { default: false });

const { formRef, validate, restoreValidation } = useNaiveForm();
const { defaultRequiredRule } = useFormRules();

const title = computed(() => (props.operateType === 'add' ? $t('common.add') : $t('common.edit')));

type Model = Pick<Api.System.Role, 'name' | 'code' | 'data_scope' | 'menuIds' | 'departmentIds' | 'status' | 'remark'>;

const model = ref<Model>(createDefaultModel());

function createDefaultModel(): Model {
  return {
    name: '',
    code: '',
    data_scope: '1',
    menuIds: [],
    departmentIds: [],
    status: '1',
    remark: ''
  };
}

type RuleKey = Extract<keyof Model, 'name' | 'code' | 'data_scope' | 'status'>;

const rules: Record<RuleKey, App.Global.FormRule> = {
  name: defaultRequiredRule,
  code: defaultRequiredRule,
  data_scope: defaultRequiredRule,
  status: defaultRequiredRule
};

const menuTreeOptions = ref<Api.System.Menu[]>([]);
const deptTreeOptions = ref<Api.System.Department[]>([]);

async function getOptions() {
  const [menuRes, deptRes] = await Promise.all([menuApi.tree(), deptApi.tree()]);

  if (!menuRes.error) {
    menuTreeOptions.value = menuRes.data ?? [];
  }

  if (!deptRes.error) {
    deptTreeOptions.value = deptRes.data ?? [];
  }
}

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    const rowData = jsonClone(props.rowData);

    Object.assign(model.value, rowData, {
      menuIds: rowData.menuIds ?? rowData.menus ?? [],
      departmentIds: rowData.departmentIds ?? rowData.departments ?? []
    });
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  if (props.operateType === 'add') {
    const { error } = await roleApi.add(model.value);

    if (!error) {
      window.$message?.success($t('common.addSuccess'));
    }
  } else if (props.rowData) {
    const { error } = await roleApi.update(props.rowData.id, model.value);

    if (!error) {
      window.$message?.success($t('common.updateSuccess'));
    }
  }

  closeDrawer();
  emit('submitted');
}

watch(visible, () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
    getOptions();
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="360">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem :label="$t('page.system.role.form.name')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.system.role.form.name')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.role.form.code')" path="code">
          <NInput v-model:value="model.code" :placeholder="$t('page.system.role.form.code')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.role.form.dataScope')" path="data_scope">
          <NSelect
            v-model:value="model.data_scope"
            :options="translateOptions(dataScopeOptions)"
            :placeholder="$t('page.system.role.form.dataScope')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.system.role.form.menus')" path="menuIds">
          <div class="max-h-240px w-full overflow-auto border border-gray-200 rounded-4px p-8px dark:border-gray-700">
            <NTree
              :data="menuTreeOptions"
              key-field="id"
              label-field="title"
              children-field="children"
              checkable
              cascade
              block-line
              default-expand-all
              :selectable="false"
              :checked-keys="model.menuIds"
              @update:checked-keys="
                keys => {
                  model.menuIds = keys.map(Number);
                }
              "
            />
          </div>
        </NFormItem>
        <NFormItem :label="$t('page.system.role.form.departments')" path="departmentIds">
          <div class="max-h-240px w-full overflow-auto border border-gray-200 rounded-4px p-8px dark:border-gray-700">
            <NTree
              ref="deptTreeRef"
              :data="deptTreeOptions"
              key-field="id"
              label-field="name"
              children-field="children"
              checkable
              cascade
              block-line
              default-expand-all
              :selectable="false"
              :checked-keys="model.departmentIds"
              @update:checked-keys="
                keys => {
                  model.departmentIds = keys.map(Number);
                }
              "
            />
          </div>
        </NFormItem>
        <NFormItem :label="$t('page.system.role.form.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in translateOptions(enableStatusOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.role.form.remark')" path="remark">
          <NInput v-model:value="model.remark" type="textarea" :placeholder="$t('page.system.role.form.remark')" />
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace :size="16">
          <NButton @click="closeDrawer">{{ $t('common.cancel') }}</NButton>
          <NButton type="primary" @click="handleSubmit">{{ $t('common.confirm') }}</NButton>
        </NSpace>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>
