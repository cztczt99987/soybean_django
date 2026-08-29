<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { $t } from '@/locales';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { enableStatusOptions, menuTypeOptions } from '@/constants/business';
import { translateOptions } from '@/utils/common';
import { menuApi } from '@/service/api';
import IconPicker from '@/components/custom/icon-picker.vue';

defineOptions({ name: 'MenuOperateModal' });

interface Props {
  /** operate type */
  operateType: NaiveUI.TableOperateType;
  /** edit row data */
  rowData?: Api.System.Menu | null;
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

type Model = Pick<
  Api.System.Menu,
  | 'parentId'
  | 'name'
  | 'title'
  | 'path'
  | 'component'
  | 'permission'
  | 'icon'
  | 'menu_type'
  | 'order'
  | 'i18n_key'
  | 'keep_alive'
  | 'hide_in_menu'
  | 'external_link'
  | 'status'
  | 'remark'
>;

const model = ref<Model>(createDefaultModel());

function createDefaultModel(): Model {
  return {
    parentId: null,
    name: '',
    title: '',
    path: '',
    component: '',
    permission: '',
    icon: '',
    menu_type: '1',
    order: 0,
    i18n_key: '',
    keep_alive: false,
    hide_in_menu: false,
    external_link: '',
    status: '1',
    remark: ''
  };
}

const rules: Partial<Record<keyof Model, App.Global.FormRule>> = {
  name: defaultRequiredRule,
  title: defaultRequiredRule,
  menu_type: defaultRequiredRule,
  status: defaultRequiredRule
};

/** menu tree options of parent menu */
const menuOptions = ref<Api.System.Menu[]>([]);

async function getMenuOptions() {
  const { data: resData, error } = await menuApi.tree();

  if (!error) {
    menuOptions.value = resData || [];
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
    const { error } = await menuApi.add(model.value);

    if (!error) {
      window.$message?.success($t('common.addSuccess'));
      closeModal();
      emit('submitted');
    }
    return;
  }

  if (props.rowData) {
    const { error } = await menuApi.update(props.rowData.id, model.value);

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
    getMenuOptions();
  }
});
</script>

<template>
  <NModal v-model:show="visible" preset="card" :title="title" class="w-480px">
    <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="80">
      <NFormItem :label="$t('page.system.menu.form.parent')" path="parentId">
        <NTreeSelect
          v-model:value="model.parentId"
          :options="menuOptions"
          key-field="id"
          label-field="title"
          children-field="children"
          clearable
        />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.name')" path="name">
        <NInput v-model:value="model.name" />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.title')" path="title">
        <NInput v-model:value="model.title" />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.path')" path="path">
        <NInput v-model:value="model.path" />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.component')" path="component">
        <NInput v-model:value="model.component" />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.permission')" path="permission">
        <NInput v-model:value="model.permission" />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.icon')" path="icon">
        <IconPicker v-model:icon="model.icon" />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.type')" path="menu_type">
        <NRadioGroup v-model:value="model.menu_type">
          <NRadio v-for="option in translateOptions(menuTypeOptions)" :key="option.value" :value="option.value">
            {{ option.label }}
          </NRadio>
        </NRadioGroup>
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.order')" path="order">
        <NInputNumber v-model:value="model.order" :min="0" class="w-full" />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.i18nKey')" path="i18n_key">
        <NInput v-model:value="model.i18n_key" />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.keepAlive')" path="keep_alive">
        <NSwitch v-model:value="model.keep_alive" />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.hideInMenu')" path="hide_in_menu">
        <NSwitch v-model:value="model.hide_in_menu" />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.externalLink')" path="external_link">
        <NInput v-model:value="model.external_link" />
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.status')" path="status">
        <NRadioGroup v-model:value="model.status">
          <NRadio v-for="option in translateOptions(enableStatusOptions)" :key="option.value" :value="option.value">
            {{ option.label }}
          </NRadio>
        </NRadioGroup>
      </NFormItem>
      <NFormItem :label="$t('page.system.menu.form.remark')" path="remark">
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
