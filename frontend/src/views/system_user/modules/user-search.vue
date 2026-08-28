<script setup lang="ts">
import { computed, ref, toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { deptApi } from '@/service/api';
import { translateOptions } from '@/utils/common';
import { $t } from '@/locales';

defineOptions({ name: 'UserSearch' });

interface Emits {
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const { formRef, validate, restoreValidation } = useNaiveForm();
const { patternRules } = useFormRules();

const model = defineModel<Api.System.UserSearchParams>('model', { required: true });

const rules = computed<Record<'phone', App.Global.FormRule>>(() => ({
  phone: patternRules.phone
}));

const deptOptions = ref<Api.System.Department[]>([]);

async function getDeptOptions() {
  const { error, data } = await deptApi.tree();

  if (!error) {
    deptOptions.value = data ?? [];
  }
}

getDeptOptions();

const defaultModel = jsonClone(toRaw(model.value));

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
      <NCollapseItem :title="$t('common.search')" name="user-search">
        <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" :label="$t('common.keywordSearch')" path="keyword">
              <NInput v-model:value="model.keyword" :placeholder="$t('common.keywordSearch')" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.system.user.form.username')" path="username">
              <NInput
                v-model:value="model.username"
                :placeholder="$t('page.system.user.form.username')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.system.user.form.nickname')" path="nickname">
              <NInput
                v-model:value="model.nickname"
                :placeholder="$t('page.system.user.form.nickname')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.system.user.form.phone')" path="phone">
              <NInput v-model:value="model.phone" :placeholder="$t('page.system.user.form.phone')" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.system.user.form.status')" path="status">
              <NSelect
                v-model:value="model.status"
                :options="translateOptions(enableStatusOptions)"
                :placeholder="$t('page.system.user.form.status')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.system.user.form.dept')" path="deptId">
              <NTreeSelect
                v-model:value="model.deptId"
                :options="deptOptions"
                key-field="id"
                label-field="name"
                :placeholder="$t('page.system.user.form.dept')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 m:6">
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
