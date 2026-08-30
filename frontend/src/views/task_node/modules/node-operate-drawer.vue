<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { taskNodeApi } from '@/service/api';
import { translateOptions } from '@/utils/common';
import { $t } from '@/locales';

defineOptions({ name: 'TaskNodeOperateDrawer' });

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Task.SchedulerNode | null;
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

type Model = Pick<
  Api.Task.SchedulerNode,
  'name' | 'node_id' | 'host' | 'port' | 'status' | 'max_concurrency' | 'remark' | 'sort_order'
>;

const model = ref<Model>(createDefaultModel());

function createDefaultModel(): Model {
  return {
    name: '',
    node_id: '',
    host: '',
    port: 8000,
    status: '1',
    max_concurrency: 4,
    remark: '',
    sort_order: 0
  };
}

const rules: Record<'name' | 'host' | 'node_id', App.Global.FormRule> = {
  name: defaultRequiredRule,
  host: defaultRequiredRule,
  node_id: defaultRequiredRule
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
    const { error } = await taskNodeApi.add(model.value);

    if (!error) {
      window.$message?.success($t('common.addSuccess'));
    }
  } else if (props.rowData) {
    const { error } = await taskNodeApi.update(props.rowData.id, model.value);

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
  <NDrawer v-model:show="visible" display-directive="show" :width="400">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="100">
        <NFormItem :label="$t('page.task.node.name')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.task.node.name')" />
        </NFormItem>
        <NFormItem :label="$t('page.task.node.nodeId')" path="node_id">
          <NInput v-model:value="model.node_id" :placeholder="$t('page.task.node.nodeIdTip')" />
        </NFormItem>
        <NFormItem :label="$t('page.task.node.host')" path="host">
          <NInput v-model:value="model.host" placeholder="127.0.0.1" />
        </NFormItem>
        <NFormItem :label="$t('page.task.node.port')" path="port">
          <NInputNumber v-model:value="model.port" :min="1" :max="65535" class="w-full" />
        </NFormItem>
        <NFormItem :label="$t('page.task.node.maxConcurrency')" path="max_concurrency">
          <NInputNumber v-model:value="model.max_concurrency" :min="1" class="w-full" />
        </NFormItem>
        <NFormItem :label="$t('page.task.job.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in translateOptions(enableStatusOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.task.job.remark')" path="remark">
          <NInput v-model:value="model.remark" type="textarea" :placeholder="$t('page.task.job.remark')" />
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
