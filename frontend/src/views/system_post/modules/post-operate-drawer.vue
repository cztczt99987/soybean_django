<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { postApi } from '@/service/api';
import { translateOptions } from '@/utils/common';
import { $t } from '@/locales';

defineOptions({ name: 'PostOperateDrawer' });

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.System.Post | null;
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

type Model = Pick<Api.System.Post, 'name' | 'code' | 'status' | 'sort_order' | 'remark'>;

const model = ref<Model>(createDefaultModel());

function createDefaultModel(): Model {
  return {
    name: '',
    code: '',
    status: '1',
    sort_order: 0,
    remark: ''
  };
}

type RuleKey = Extract<keyof Model, 'name' | 'code' | 'status'>;

const rules: Record<RuleKey, App.Global.FormRule> = {
  name: defaultRequiredRule,
  code: defaultRequiredRule,
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
    const { error } = await postApi.add(model.value);

    if (!error) {
      window.$message?.success($t('common.addSuccess'));
    }
  } else if (props.rowData) {
    const { error } = await postApi.update(props.rowData.id, model.value);

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
        <NFormItem :label="$t('page.system.post.form.name')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.system.post.form.name')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.post.form.code')" path="code">
          <NInput v-model:value="model.code" :placeholder="$t('page.system.post.form.code')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.post.form.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in translateOptions(enableStatusOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.post.form.sortOrder')" path="sort_order">
          <NInputNumber v-model:value="model.sort_order" :min="0" class="w-full" />
        </NFormItem>
        <NFormItem :label="$t('page.system.post.form.remark')" path="remark">
          <NInput v-model:value="model.remark" type="textarea" :placeholder="$t('page.system.post.form.remark')" />
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
