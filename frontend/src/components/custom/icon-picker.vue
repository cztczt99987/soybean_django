<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { $t } from '@/locales';
import { iconPickerCategories } from '@/constants/icon';
import SvgIcon from './svg-icon.vue';

defineOptions({ name: 'IconPicker' });

/** iconify icon name, e.g. "mdi:cog" */
const icon = defineModel<string>({ default: '' });

const visible = ref(false);
const keyword = ref('');
const activeCategory = ref(iconPickerCategories[0].key);
const selected = ref('');

watch(visible, val => {
  if (val) {
    selected.value = icon.value;
    keyword.value = '';
    activeCategory.value = iconPickerCategories[0].key;
  }
});

const allIcons = computed(() => iconPickerCategories.flatMap(category => category.icons));

const displayIcons = computed(() => {
  const kw = keyword.value.trim().toLowerCase();
  if (kw) {
    return allIcons.value.filter(name => name.toLowerCase().includes(kw));
  }
  return iconPickerCategories.find(category => category.key === activeCategory.value)?.icons ?? [];
});

function handleSelect(name: string) {
  selected.value = selected.value === name ? '' : name;
}

function handleConfirm() {
  icon.value = selected.value;
  visible.value = false;
}

function handleClear() {
  icon.value = '';
  selected.value = '';
  visible.value = false;
}
</script>

<template>
  <div>
    <NInputGroup>
      <NInput v-model:value="icon" clearable>
        <template #prefix>
          <SvgIcon v-if="icon" :icon="icon" class="text-16px" />
        </template>
      </NInput>
      <NButton @click="visible = true">{{ $t('common.iconPicker.title') }}</NButton>
    </NInputGroup>

    <NModal v-model:show="visible" preset="card" :title="$t('common.iconPicker.title')" class="w-600px">
      <div class="flex-col-stretch gap-12px">
        <div class="flex items-center gap-12px">
          <NInput
            v-model:value="keyword"
            :placeholder="$t('common.iconPicker.search')"
            clearable
            class="flex-1"
          >
            <template #prefix>
              <SvgIcon icon="mdi:magnify" class="text-16px text-gray-400" />
            </template>
          </NInput>
          <NTabs v-model:value="activeCategory" type="segment" size="small" class="flex-1">
            <NTab
              v-for="category in iconPickerCategories"
              :key="category.key"
              :name="category.key"
              :disabled="!!keyword.trim()"
            >
              {{ $t(category.i18nKey) }}
            </NTab>
          </NTabs>
        </div>

        <div
          v-if="displayIcons.length"
          class="grid grid-cols-8 gap-8px max-h-360px min-h-200px overflow-auto border border-gray-200 rounded-4px p-8px dark:border-gray-700"
        >
          <button
            v-for="name in displayIcons"
            :key="name"
            type="button"
            :title="name"
            class="flex-center h-36px cursor-pointer border border-transparent rounded-4px text-20px hover:bg-gray-100 dark:hover:bg-gray-700"
            :class="{ 'border-primary text-primary bg-primary bg-opacity-10': name === selected }"
            @click="handleSelect(name)"
          >
            <SvgIcon :icon="name" />
          </button>
        </div>
        <div v-else class="flex-center h-200px">
          <NEmpty :description="$t('common.noData')" />
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center gap-8px">
            <template v-if="selected">
              <SvgIcon :icon="selected" class="text-24px" />
              <span class="text-12px text-gray-500">{{ selected }}</span>
            </template>
          </div>
          <NSpace>
            <NButton @click="handleClear">{{ $t('common.iconPicker.clear') }}</NButton>
            <NButton @click="visible = false">{{ $t('common.cancel') }}</NButton>
            <NButton type="primary" @click="handleConfirm">{{ $t('common.confirm') }}</NButton>
          </NSpace>
        </div>
      </div>
    </NModal>
  </div>
</template>

<style scoped></style>
