<script setup lang="tsx">
import { computed, reactive, ref } from 'vue';
import { NButton, NPopconfirm, NProgress, NTag } from 'naive-ui';
import dayjs from 'dayjs';
import { fileApi, storageApi } from '@/service/api';
import { $t } from '@/locales';

defineOptions({ name: 'MonitorFile' });

type FileEntry = Api.Monitor.FileEntry;
type StorageType = Api.Monitor.StorageType;

/** 字节格式化 */
function formatBytes(n: number): string {
  if (!n || n <= 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(n) / Math.log(1024));
  return `${(n / 1024 ** i).toFixed(2)} ${units[i]}`;
}

const storageTypeLabel: Record<StorageType, () => string> = {
  local: () => $t('page.monitor.file.typeLocal'),
  aliyun: () => $t('page.monitor.file.typeAliyun'),
  tencent: () => $t('page.monitor.file.typeTencent'),
  qiniu: () => $t('page.monitor.file.typeQiniu')
};

/** 各存储类型的字段列表 */
type StorageFieldKey =
  | 'basePath'
  | 'endpoint'
  | 'bucket'
  | 'accessKeyId'
  | 'accessKeySecret'
  | 'region'
  | 'secretId'
  | 'secretKey'
  | 'zone'
  | 'accessKey'
  | 'customDomain';

const storageFields: Record<StorageType, Array<{ key: StorageFieldKey; secret?: boolean }>> = {
  local: [{ key: 'basePath' }],
  aliyun: [
    { key: 'endpoint' },
    { key: 'bucket' },
    { key: 'accessKeyId' },
    { key: 'accessKeySecret', secret: true },
    { key: 'customDomain' }
  ],
  tencent: [
    { key: 'region' },
    { key: 'bucket' },
    { key: 'secretId' },
    { key: 'secretKey', secret: true },
    { key: 'customDomain' }
  ],
  qiniu: [
    { key: 'zone' },
    { key: 'bucket' },
    { key: 'accessKey' },
    { key: 'secretKey', secret: true },
    { key: 'customDomain' }
  ]
};

// ===================== Tab1 目录浏览 =====================

const fileLoading = ref(false);
const currentPath = ref('');
const parentPath = ref<string | null>(null);
const entries = ref<FileEntry[]>([]);
const disk = ref<{ total: number; used: number; free: number }>({ total: 0, used: 0, free: 0 });

const diskPercent = computed(() => (disk.value.total ? Math.round((disk.value.used / disk.value.total) * 100) : 0));

const breadcrumbItems = computed(() => {
  const items: Array<{ label: string; path: string }> = [{ label: $t('page.monitor.file.root'), path: '' }];
  if (currentPath.value && currentPath.value !== '.') {
    const segs = currentPath.value.split('/').filter(Boolean);
    let acc = '';
    for (const seg of segs) {
      acc = acc ? `${acc}/${seg}` : seg;
      items.push({ label: seg, path: acc });
    }
  }
  return items;
});

async function loadFiles(path: string) {
  fileLoading.value = true;
  try {
    const { data, error } = await fileApi.list(path);
    if (!error && data) {
      currentPath.value = data.currentPath;
      parentPath.value = data.parentPath;
      entries.value = data.entries ?? [];
      disk.value = data.disk ?? { total: 0, used: 0, free: 0 };
    }
  } finally {
    fileLoading.value = false;
  }
}

function enterDir(entry: FileEntry) {
  loadFiles(entry.path);
}

function goUp() {
  if (parentPath.value !== null) {
    loadFiles(parentPath.value);
  }
}

function goToPath(path: string) {
  loadFiles(path);
}

async function handleDownload(entry: FileEntry) {
  const { data, error } = await fileApi.download(entry.path);
  if (!error && data) {
    const url = window.URL.createObjectURL(data);
    const link = document.createElement('a');
    link.href = url;
    link.download = entry.name;
    document.body.append(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }
}

const fileColumns = computed<NaiveUI.TableColumn<FileEntry>[]>(() => [
  {
    key: 'name',
    title: $t('page.monitor.file.name'),
    align: 'center',
    minWidth: 260,
    render: row => (
      <div class="flex-center gap-8px justify-start">
        {row.isDir ? <icon-mdi-folder class="text-icon text-warning" /> : <icon-mdi-file-document-outline class="text-icon" />}
        {row.isDir ? (
          <button class="truncate text-left hover:text-primary" onClick={() => enterDir(row)}>
            {row.name}
          </button>
        ) : (
          <span class="truncate">{row.name}</span>
        )}
      </div>
    )
  },
  {
    key: 'size',
    title: $t('page.monitor.file.size'),
    align: 'center',
    width: 120,
    render: row => (row.isDir ? '-' : formatBytes(row.size))
  },
  {
    key: 'modified',
    title: $t('page.monitor.file.modified'),
    align: 'center',
    width: 180,
    render: row => dayjs.unix(row.modified).format('YYYY-MM-DD HH:mm:ss')
  },
  {
    key: 'operate',
    title: $t('common.operate'),
    align: 'center',
    width: 100,
    render: row =>
      row.isDir ? null : (
        <NButton type="primary" ghost size="small" onClick={() => handleDownload(row)}>
          {$t('page.monitor.file.download')}
        </NButton>
      )
  }
]);

// ===================== Tab2 存储配置 =====================

const storageLoading = ref(false);
const saving = ref(false);
const activeStorage = ref<StorageType>('local');
const selectedType = ref<StorageType>('local');
const storageModel = reactive<Record<string, string>>({});

async function loadStorage(type: StorageType) {
  storageLoading.value = true;
  try {
    const { data, error } = await storageApi.get(type);
    if (!error && data) {
      activeStorage.value = data.active;
      selectedType.value = type;
      const next: Record<string, string> = {};
      storageFields[type].forEach(f => {
        next[f.key] = String(data.config?.[f.key] ?? '');
      });
      Object.assign(storageModel, next);
    }
  } finally {
    storageLoading.value = false;
  }
}

/** 仅取当前存储类型相关字段 */
function currentPayload(): Record<string, string> {
  const payload: Record<string, string> = {};
  storageFields[selectedType.value].forEach(f => {
    payload[f.key] = storageModel[f.key] ?? '';
  });
  return payload;
}

function switchType(type: StorageType) {
  loadStorage(type);
}

async function handleValidate() {
  const { error } = await storageApi.validate(selectedType.value, currentPayload());
  if (!error) {
    window.$message?.success($t('page.monitor.file.validateSuccess'));
  }
}

async function handleSave() {
  saving.value = true;
  try {
    const { error } = await storageApi.save(selectedType.value, currentPayload());
    if (!error) {
      window.$message?.success($t('page.monitor.file.saveSuccess'));
    }
  } finally {
    saving.value = false;
  }
}

async function handleSwitchActive() {
  const { error } = await storageApi.switchActive(selectedType.value);
  if (!error) {
    window.$message?.success($t('page.monitor.file.switchSuccess'));
    activeStorage.value = selectedType.value;
  }
}

// ===================== 初始化 =====================

function onTabChange(name: string) {
  if (name === 'storage' && !Object.keys(storageModel).length) {
    loadStorage(activeStorage.value);
  }
}

loadFiles('');
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NCard :title="$t('page.monitor.file.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <NTabs type="line" animated class="h-full flex-col-stretch" @update:value="onTabChange">
        <NTabPane name="browser" :tab="$t('page.monitor.file.browser')" class="h-full flex-col-stretch">
          <NSpace vertical :size="12">
            <div class="flex-center justify-between flex-wrap gap-8px">
              <NBreadcrumb>
                <NBreadcrumbItem v-for="item in breadcrumbItems" :key="item.path">
                  <a class="cursor-pointer hover:text-primary" @click="goToPath(item.path)">{{ item.label }}</a>
                </NBreadcrumbItem>
              </NBreadcrumb>
              <NSpace>
                <NButton size="small" :disabled="parentPath === null" @click="goUp">
                  <template #icon>
                    <icon-mdi-arrow-up class="text-icon" />
                  </template>
                  {{ $t('page.monitor.file.up') }}
                </NButton>
                <NButton size="small" @click="loadFiles(currentPath)">
                  <template #icon>
                    <icon-mdi-refresh class="text-icon" :class="{ 'animate-spin': fileLoading }" />
                  </template>
                  {{ $t('common.refresh') }}
                </NButton>
              </NSpace>
            </div>
            <div class="flex-center gap-12px">
              <span class="text-12px text-gray-500">{{ formatBytes(disk.used) }} / {{ formatBytes(disk.total) }}</span>
              <NProgress type="line" :percentage="diskPercent" :show-indicator="false" class="flex-1" />
            </div>
          </NSpace>
          <NDataTable
            :columns="fileColumns"
            :data="entries"
            size="small"
            :loading="fileLoading"
            :row-key="(row: FileEntry) => row.path"
            :pagination="false"
            class="mt-12px flex-1"
          />
        </NTabPane>

        <NTabPane name="storage" :tab="$t('page.monitor.file.storage')">
          <NSpace vertical :size="16" class="w-full">
            <NSpace align="center" wrap>
              <span>{{ $t('page.monitor.file.currentActive') }}</span>
              <NTag type="success">{{ storageTypeLabel[activeStorage]() }}</NTag>
            </NSpace>
            <NSpace wrap>
              <NButton
                v-for="t in (['local', 'aliyun', 'tencent', 'qiniu'] as StorageType[])"
                :key="t"
                size="small"
                :type="selectedType === t ? 'primary' : 'default'"
                :ghost="selectedType === t"
                @click="switchType(t)"
              >
                {{ storageTypeLabel[t]() }}
              </NButton>
            </NSpace>
            <NSpin :show="storageLoading">
              <NForm label-placement="left" :label-width="160" class="max-w-560px">
                <NFormItem
                  v-for="field in storageFields[selectedType]"
                  :key="field.key"
                  :label="$t(`page.monitor.file.fields.${field.key}`)"
                >
                  <NInput
                    v-if="field.secret"
                    v-model:value="storageModel[field.key]"
                    type="password"
                    show-password-on="click"
                  />
                  <NInput v-else v-model:value="storageModel[field.key]" />
                </NFormItem>
              </NForm>
            </NSpin>
            <NSpace>
              <NButton @click="handleValidate">{{ $t('page.monitor.file.validate') }}</NButton>
              <NButton type="primary" :loading="saving" @click="handleSave">{{ $t('page.monitor.file.save') }}</NButton>
              <NPopconfirm @positive-click="handleSwitchActive">
                <template #trigger>
                  <NButton type="warning" ghost>{{ $t('page.monitor.file.switchTo') }}</NButton>
                </template>
                {{ $t('page.monitor.file.switchConfirm') }}
              </NPopconfirm>
            </NSpace>
          </NSpace>
        </NTabPane>
      </NTabs>
    </NCard>
  </div>
</template>

<style scoped></style>
