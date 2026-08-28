<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { dictDataApi } from '@/service/api';
import { translateOptions } from '@/utils/common';
import { $t } from '@/locales';

defineOptions({ name: 'DictDataOperateDrawer' });

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.System.DictData | null;
  /** 新增时归属的字典类型主键 */
  dictTypeId?: number | null;
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

type Model = Pick<Api.System.DictData, 'label' | 'value' | 'css_class' | 'list_class' | 'is_default' | 'status'>;

const model = ref<Model>(createDefaultModel());

function createDefaultModel(): Model {
  return {
    label: '',
    value: '',
    css_class: '',
    list_class: '',
    is_default: false,
    status: '1'
  };
}

type RuleKey = Extract<keyof Model, 'label' | 'value' | 'status'>;

const rules: Record<RuleKey, App.Global.FormRule> = {
  label: defaultRequiredRule,
  value: defaultRequiredRule,
  status: defaultRequiredRule
};

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
    const { error } = await dictDataApi.add({ ...model.value, dict_type: props.dictTypeId });

    if (!error) {
      window.$message?.success($t('common.addSuccess'));
    }
  } else if (props.rowData) {
    const { error } = await dictDataApi.update(props.rowData.id, model.value);

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
        <NFormItem :label="$t('page.system.dict.data.label')" path="label">
          <NInput v-model:value="model.label" :placeholder="$t('page.system.dict.data.label')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.value')" path="value">
          <NInput v-model:value="model.value" :placeholder="$t('page.system.dict.data.value')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.cssClass')" path="css_class">
          <NInput v-model:value="model.css_class" :placeholder="$t('page.system.dict.data.cssClass')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.listClass')" path="list_class">
          <NInput v-model:value="model.list_class" :placeholder="$t('page.system.dict.data.listClass')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.isDefault')" path="is_default">
          <NSwitch v-model:value="model.is_default" />
        </NFormItem>
        <NFormItem :label="$t('page.system.dict.data.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in translateOptions(enableStatusOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
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
