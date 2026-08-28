<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions, valueTypeOptions } from '@/constants/business';
import { yesOrNoOptions } from '@/constants/common';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { configApi } from '@/service/api';
import { translateOptions } from '@/utils/common';
import { $t } from '@/locales';

defineOptions({ name: 'ConfigOperateDrawer' });

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.System.Config | null;
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

type Model = Pick<Api.System.Config, 'name' | 'code' | 'value' | 'value_type' | 'is_system' | 'status' | 'remark'>;

const model = ref<Model>(createDefaultModel());

function createDefaultModel(): Model {
  return {
    name: '',
    code: '',
    value: '',
    value_type: 'S',
    is_system: false,
    status: '1',
    remark: ''
  };
}

type RuleKey = Extract<keyof Model, 'name' | 'code' | 'value' | 'value_type' | 'status'>;

const rules: Record<RuleKey, App.Global.FormRule> = {
  name: defaultRequiredRule,
  code: defaultRequiredRule,
  value: defaultRequiredRule,
  value_type: defaultRequiredRule,
  status: defaultRequiredRule
};

function handleIsSystemChange(val: string | number | boolean) {
  model.value.is_system = val === 'Y';
}

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    Object.assign(model.value, jsonClone(props.rowData));
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  if (props.operateType === 'add') {
    const { error } = await configApi.add(model.value);

    if (!error) {
      window.$message?.success($t('common.addSuccess'));
    }
  } else if (props.rowData) {
    const { error } = await configApi.update(props.rowData.id, model.value);

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
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="360">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem :label="$t('page.system.config.form.name')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.system.config.form.name')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.code')" path="code">
          <NInput v-model:value="model.code" :placeholder="$t('page.system.config.form.code')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.value')" path="value">
          <NInput v-model:value="model.value" type="textarea" :placeholder="$t('page.system.config.form.value')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.valueType')" path="value_type">
          <NSelect
            v-model:value="model.value_type"
            :options="translateOptions(valueTypeOptions)"
            :placeholder="$t('page.system.config.form.valueType')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.isSystem')" path="is_system">
          <NRadioGroup :value="model.is_system ? 'Y' : 'N'" @update:value="handleIsSystemChange">
            <NRadio v-for="item in translateOptions(yesOrNoOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in translateOptions(enableStatusOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.config.form.remark')" path="remark">
          <NInput v-model:value="model.remark" type="textarea" :placeholder="$t('page.system.config.form.remark')" />
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
