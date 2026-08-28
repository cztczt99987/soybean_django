<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { $t } from '@/locales';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { enableStatusOptions } from '@/constants/business';
import { translateOptions } from '@/utils/common';
import { deptApi } from '@/service/api';

defineOptions({ name: 'DeptOperateModal' });

interface Props {
  /** operate type */
  operateType: NaiveUI.TableOperateType;
  /** edit row data */
  rowData?: Api.System.Department | null;
}

interface Emits {
  (e: 'submitted'): void;
}

const props = defineProps<Props>();

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', { default: false });

const { formRef, validate, restoreValidation } = useNaiveForm();
const { defaultRequiredRule } = useFormRules();

const title = computed(() => (props.operateType === 'add' ? $t('common.add') : $t('common.edit')));

type Model = Pick<Api.System.Department, 'parentId' | 'name' | 'code' | 'leader' | 'phone' | 'email' | 'status' | 'remark'>;

const model = ref<Model>(createDefaultModel());

function createDefaultModel(): Model {
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

const rules: Partial<Record<keyof Model, App.Global.FormRule>> = {
  name: defaultRequiredRule,
  code: defaultRequiredRule,
  status: defaultRequiredRule
};

/** dept tree options of parent dept */
const deptOptions = ref<Api.System.Department[]>([]);

async function getDeptOptions() {
  const { data: resData, error } = await deptApi.tree();

  if (!error) {
    deptOptions.value = resData || [];
  }
}

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'add' && props.rowData) {
    model.value.parentId = props.rowData.id;
  }

  if (props.operateType === 'edit' && props.rowData) {
    Object.assign(model.value, jsonClone(props.rowData));
  }
}

function closeModal() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  if (props.operateType === 'add') {
    const { error } = await deptApi.add(model.value);

    if (!error) {
      window.$message?.success($t('common.addSuccess'));
      closeModal();
      emit('submitted');
    }
    return;
  }

  if (props.rowData) {
    const { error } = await deptApi.update(props.rowData.id, model.value);

    if (!error) {
      window.$message?.success($t('common.updateSuccess'));
      closeModal();
      emit('submitted');
    }
  }
}

watch(visible, () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
    getDeptOptions();
  }
});
</script>

<template>
  <NModal v-model:show="visible" preset="card" :title="title" class="w-480px">
    <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="80">
      <NFormItem :label="$t('page.system.dept.form.parent')" path="parentId">
        <NTreeSelect
          v-model:value="model.parentId"
          :options="deptOptions"
          key-field="id"
          label-field="name"
          children-field="children"
          clearable
        />
      </NFormItem>
      <NFormItem :label="$t('page.system.dept.form.name')" path="name">
        <NInput v-model:value="model.name" />
      </NFormItem>
      <NFormItem :label="$t('page.system.dept.form.code')" path="code">
        <NInput v-model:value="model.code" />
      </NFormItem>
      <NFormItem :label="$t('page.system.dept.form.leader')" path="leader">
        <NInput v-model:value="model.leader" />
      </NFormItem>
      <NFormItem :label="$t('page.system.dept.form.phone')" path="phone">
        <NInput v-model:value="model.phone" />
      </NFormItem>
      <NFormItem :label="$t('page.system.dept.form.email')" path="email">
        <NInput v-model:value="model.email" />
      </NFormItem>
      <NFormItem :label="$t('page.system.dept.form.status')" path="status">
        <NRadioGroup v-model:value="model.status">
          <NRadio v-for="option in translateOptions(enableStatusOptions)" :key="option.value" :value="option.value">
            {{ option.label }}
          </NRadio>
        </NRadioGroup>
      </NFormItem>
      <NFormItem :label="$t('page.system.dept.form.remark')" path="remark">
        <NInput v-model:value="model.remark" type="textarea" />
      </NFormItem>
    </NForm>
    <template #footer>
      <NSpace justify="end">
        <NButton size="large" @click="closeModal">{{ $t('common.cancel') }}</NButton>
        <NButton size="large" type="primary" @click="handleSubmit">{{ $t('common.confirm') }}</NButton>
      </NSpace>
    </template>
  </NModal>
</template>
