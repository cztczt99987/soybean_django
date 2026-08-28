<script setup lang="ts">
import { computed, toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { operationTypeOptions } from '@/constants/business';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { translateOptions } from '@/utils/common';
import { $t } from '@/locales';

defineOptions({ name: 'LogSearch' });

interface Emits {
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const { formRef, validate, restoreValidation } = useNaiveForm();

const model = defineModel<Api.System.LogSearchParams>('model', { required: true });

/** 日志状态选项（成功/失败，文案与启用状态不同） */
const logStatusOptions = computed(() => [
  { label: $t('page.system.common.success'), value: '1' },
  { label: $t('page.system.common.failure'), value: '0' }
]);

const rules = computed(() => {
  const { patternRules } = useFormRules();

  return {
    username: patternRules.userName
  };
});

const defaultModel = jsonClone(toRaw(model.value));

/** 日期范围：beginTime/endTime 与 NDatePicker formatted-value 的双向代理 */
const dateRange = computed<[string, string] | null>({
  get: () => {
    if (model.value.beginTime && model.value.endTime) {
      const range: [string, string] = [model.value.beginTime, model.value.endTime];
      return range;
    }
    return null;
  },
  set: (val: [string, string] | null) => {
    model.value.beginTime = val?.[0] ?? null;
    model.value.endTime = val?.[1] ?? null;
  }
});

function resetModel() {
  Object.assign(model.value, defaultModel);
}

async function reset() {
  await restoreValidation();
  resetModel();
}

async function search() {
  await validate();
  emit('search');
}
</script>

<template>
  <NCard :bordered="false" size="small" class="card-wrapper">
    <NCollapse>
      <NCollapseItem :title="$t('common.search')" name="log-search">
        <NForm
          ref="formRef"
          :model="model"
          :rules="rules"
          label-placement="left"
          :label-width="90"
        >
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.system.log.fields.username')"
              path="username"
              class="pr-24px"
            >
              <NInput v-model:value="model.username" :placeholder="$t('page.system.log.fields.username')" />
            </NFormItemGi>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.system.log.fields.module')"
              path="module"
              class="pr-24px"
            >
              <NInput v-model:value="model.module" :placeholder="$t('page.system.log.fields.module')" />
            </NFormItemGi>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.system.log.fields.description')"
              path="description"
              class="pr-24px"
            >
              <NInput v-model:value="model.description" :placeholder="$t('page.system.log.fields.description')" />
            </NFormItemGi>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.system.log.fields.operationType')"
              path="operationType"
              class="pr-24px"
            >
              <NSelect
                v-model:value="model.operationType"
                :options="translateOptions(operationTypeOptions)"
                :placeholder="$t('page.system.log.fields.operationType')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.system.log.fields.status')" path="status" class="pr-24px">
              <NSelect
                v-model:value="model.status"
                :options="logStatusOptions"
                :placeholder="$t('page.system.log.fields.status')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.system.log.fields.dateRange')"
              path="dateRange"
              class="pr-24px"
            >
              <NDatePicker
                v-model:formatted-value="dateRange"
                type="daterange"
                value-format="yyyy-MM-dd"
                clearable
                class="w-full"
              />
            </NFormItemGi>
            <NFormItemGi span="24 m:6" class="pr-24px">
              <NSpace class="w-full" justify="end">
                <NButton @click="reset">
                  <template #icon>
                    <icon-ic-round-refresh class="text-icon" />
                  </template>
                  {{ $t('common.reset') }}
                </NButton>
                <NButton type="primary" ghost @click="search">
                  <template #icon>
                    <icon-ic-round-search class="text-icon" />
                  </template>
                  {{ $t('common.search') }}
                </NButton>
              </NSpace>
            </NFormItemGi>
          </NGrid>
        </NForm>
      </NCollapseItem>
    </NCollapse>
  </NCard>
</template>

<style scoped></style>
