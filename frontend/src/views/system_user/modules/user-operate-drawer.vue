<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions, userGenderOptions } from '@/constants/business';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { deptApi, postApi, roleApi, userApi } from '@/service/api';
import { translateOptions } from '@/utils/common';
import { $t } from '@/locales';

defineOptions({ name: 'UserOperateDrawer' });

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.System.User | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', { default: false });

const { formRef, validate, restoreValidation } = useNaiveForm();
const { patternRules, defaultRequiredRule } = useFormRules();

const title = computed(() => (props.operateType === 'add' ? $t('common.add') : $t('common.edit')));

type Model = Pick<
  Api.System.User,
  | 'username'
  | 'nickname'
  | 'password'
  | 'email'
  | 'phone'
  | 'gender'
  | 'department_id'
  | 'roleIds'
  | 'postIds'
  | 'status'
  | 'remark'
>;

const model = ref<Model>(createDefaultModel());

function createDefaultModel(): Model {
  return {
    username: '',
    nickname: '',
    password: '',
    email: '',
    phone: '',
    gender: '0',
    department_id: null,
    roleIds: [],
    postIds: [],
    status: '1',
    remark: ''
  };
}

type RuleKey = Extract<keyof Model, 'username' | 'nickname' | 'password' | 'email' | 'phone' | 'status'>;

const rules: Record<RuleKey, App.Global.FormRule> = {
  username: defaultRequiredRule,
  nickname: defaultRequiredRule,
  password: defaultRequiredRule,
  email: patternRules.email,
  phone: patternRules.phone,
  status: defaultRequiredRule
};

const deptOptions = ref<Api.System.Department[]>([]);
const roleOptions = ref<{ label: string; value: number }[]>([]);
const postOptions = ref<{ label: string; value: number }[]>([]);

async function getOptions() {
  const [deptRes, roleRes, postRes] = await Promise.all([deptApi.tree(), roleApi.options(), postApi.options()]);

  if (!deptRes.error) {
    deptOptions.value = deptRes.data ?? [];
  }

  if (!roleRes.error) {
    roleOptions.value = (roleRes.data ?? []).map(item => ({ label: item.name, value: item.id }));
  }

  if (!postRes.error) {
    postOptions.value = (postRes.data ?? []).map(item => ({ label: item.name, value: item.id }));
  }
}

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    const rowData = jsonClone(props.rowData);

    Object.assign(model.value, rowData, {
      roleIds: rowData.roles?.map(role => role.id) ?? [],
      postIds: rowData.posts?.map(post => post.id) ?? []
    });
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  if (props.operateType === 'add') {
    const { error } = await userApi.add(model.value);

    if (!error) {
      window.$message?.success($t('common.addSuccess'));
    }
  } else if (props.rowData) {
    const payload = { ...model.value };
    delete payload.password;

    const { error } = await userApi.update(props.rowData.id, payload);

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
        <NFormItem :label="$t('page.system.user.form.username')" path="username">
          <NInput v-model:value="model.username" :placeholder="$t('page.system.user.form.username')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.user.form.nickname')" path="nickname">
          <NInput v-model:value="model.nickname" :placeholder="$t('page.system.user.form.nickname')" />
        </NFormItem>
        <NFormItem
          v-if="operateType === 'add'"
          :label="$t('page.system.user.form.password')"
          path="password"
        >
          <NInput
            v-model:value="model.password"
            type="password"
            show-password-on="click"
            :placeholder="$t('page.system.user.form.password')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.system.user.form.email')" path="email">
          <NInput v-model:value="model.email" :placeholder="$t('page.system.user.form.email')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.user.form.phone')" path="phone">
          <NInput v-model:value="model.phone" :placeholder="$t('page.system.user.form.phone')" />
        </NFormItem>
        <NFormItem :label="$t('page.system.user.form.gender')" path="gender">
          <NRadioGroup v-model:value="model.gender">
            <NRadio v-for="item in translateOptions(userGenderOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.user.form.dept')" path="department_id">
          <NTreeSelect
            v-model:value="model.department_id"
            :options="deptOptions"
            key-field="id"
            label-field="name"
            :placeholder="$t('page.system.user.form.dept')"
            clearable
          />
        </NFormItem>
        <NFormItem :label="$t('page.system.user.form.roles')" path="roleIds">
          <NSelect
            v-model:value="model.roleIds"
            multiple
            :options="roleOptions"
            :placeholder="$t('page.system.user.form.roles')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.system.user.form.posts')" path="postIds">
          <NSelect
            v-model:value="model.postIds"
            multiple
            :options="postOptions"
            :placeholder="$t('page.system.user.form.posts')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.system.user.form.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in translateOptions(enableStatusOptions)" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.system.user.form.remark')" path="remark">
          <NInput v-model:value="model.remark" type="textarea" :placeholder="$t('page.system.user.form.remark')" />
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
