<script setup lang="ts">
import { ref } from 'vue';
import { getSwaggerDocsUrl } from '@/service/api';

defineOptions({ name: 'ApiDocs' });

const docsUrl = getSwaggerDocsUrl();
const loading = ref(true);

function handleLoad() {
  loading.value = false;
}
</script>

<template>
  <div class="relative h-full min-h-500px">
    <iframe :src="docsUrl" class="size-full border-0" allow="fullscreen" @load="handleLoad" />
    <div v-show="loading" class="absolute inset-0 flex-center bg-layout">
      <NSpin size="medium" />
    </div>
  </div>
</template>
