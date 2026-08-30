<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { jobTypeOptions, taskPriorityOptions, triggerTypeOptions } from '@/constants/task';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { taskJobApi } from '@/service/api';
import { translateOptions } from '@/utils/common';
import { $t } from '@/locales';

defineOptions({ name: 'TaskJobOperateDrawer' });

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Task.TaskJob | null;
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

/** 内置处理器清单 */
const handlerOptions = ref<{ key: string; label: string }[]>([]);

type Model = Pick<
  Api.Task.TaskJob,
  | 'name'
  | 'description'
  | 'job_type'
  | 'handler'
  | 'http_method'
  | 'http_url'
  | 'http_body'
  | 'trigger_type'
  | 'cron_expr'
  | 'interval_seconds'
  | 'run_date'
  | 'priority'
  | 'timeout_seconds'
  | 'status'
  | 'sort_order'
  | 'remark'
>;

const model = ref<Model>(createDefaultModel());

function createDefaultModel(): Model {
  return {
    name: '',
    description: '',
    job_type: 'function',
    handler: 'demo_heartbeat',
    http_method: 'GET',
    http_url: '',
    http_body: '',
    trigger_type: 'cron',
    cron_expr: '',
    interval_seconds: 60,
    run_date: null,
    priority: '2',
    timeout_seconds: 300,
    status: '1',
    sort_order: 0,
    remark: ''
  };
}

type RuleKey = Extract<keyof Model, 'name' | 'trigger_type'>;

const rules: Record<RuleKey, App.Global.FormRule> = {
  name: defaultRequiredRule,
  trigger_type: defaultRequiredRule
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
    const { error } = await taskJobApi.add(model.value);

    if (!error) {
      window.$message?.success($t('common.addSuccess'));
    }
  } else if (props.rowData) {
    const { error } = await taskJobApi.update(props.rowData.id, model.value);

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

    taskJobApi.handlers().then(({ data, error }) => {
      if (!error) {
        handlerOptions.value = data || [];
      }
    });
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="480">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="100">
        <NFormItem :label="$t('page.task.job.name')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.task.job.namePlaceholder')" />
        </NFormItem>
        <NFormItem :label="$t('page.task.job.description')" path="description">
          <NInput v-model:value="model.description" :placeholder="$t('page.task.job.description')" />
        </NFormItem>
        <NFormItem :label="$t('page.task.job.jobType')" path="job_type">
          <NRadioGroup v-model:value="model.job_type">
            <NRadio v-for="item in translateOptions(jobTypeOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem v-if="model.job_type === 'function'" :label="$t('page.task.job.handler')" path="handler">
          <NSelect
            v-model:value="model.handler"
            :options="handlerOptions.map(item => ({ label: `${item.label} (${item.key})`, value: item.key }))"
            :placeholder="$t('page.task.job.handler')"
          />
        </NFormItem>
        <template v-if="model.job_type === 'http'">
          <NFormItem :label="$t('page.task.job.httpMethod')" path="http_method">
            <NSelect
              v-model:value="model.http_method"
              :options="['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].map(item => ({ label: item, value: item }))"
            />
          </NFormItem>
          <NFormItem :label="$t('page.task.job.httpUrl')" path="http_url">
            <NInput v-model:value="model.http_url" placeholder="https://..." />
          </NFormItem>
          <NFormItem :label="$t('page.task.job.httpBody')" path="http_body">
            <NInput v-model:value="model.http_body" type="textarea" :rows="2" :placeholder="$t('page.task.job.httpBody')" />
          </NFormItem>
        </template>
        <NFormItem :label="$t('page.task.job.triggerType')" path="trigger_type">
          <NRadioGroup v-model:value="model.trigger_type">
            <NRadio v-for="item in translateOptions(triggerTypeOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem
          v-if="model.trigger_type === 'cron'"
          :label="$t('page.task.job.cronExpr')"
          path="cron_expr"
          :rule="{ required: true, message: $t('page.task.job.cronRule') }"
        >
          <NInput v-model:value="model.cron_expr" placeholder="0 3 * * *" />
        </NFormItem>
        <NFormItem v-if="model.trigger_type === 'interval'" :label="$t('page.task.job.intervalSeconds')" path="interval_seconds">
          <NInputNumber v-model:value="model.interval_seconds" :min="5" class="w-full">
            <template #suffix>s</template>
          </NInputNumber>
        </NFormItem>
        <NFormItem v-if="model.trigger_type === 'date'" :label="$t('page.task.job.runDate')" path="run_date">
          <NDatePicker
            v-model:formatted-value="model.run_date"
            type="datetime"
            value-format="yyyy-MM-dd HH:mm:ss"
            class="w-full"
          />
        </NFormItem>
        <NFormItem :label="$t('page.task.job.priority')" path="priority">
          <NRadioGroup v-model:value="model.priority">
            <NRadio v-for="item in translateOptions(taskPriorityOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.task.job.timeout')" path="timeout_seconds">
          <NInputNumber v-model:value="model.timeout_seconds" :min="1" class="w-full">
            <template #suffix>s</template>
          </NInputNumber>
        </NFormItem>
        <NFormItem :label="$t('page.task.job.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in translateOptions(enableStatusOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.task.job.sortOrder')" path="sort_order">
          <NInputNumber v-model:value="model.sort_order" class="w-full" />
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
