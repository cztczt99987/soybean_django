import type { Router } from 'vue-router';
import { useTitle } from '@vueuse/core';
import { $t } from '@/locales';
import { useAppStore } from '@/store/modules/app';

export function createDocumentTitleGuard(router: Router) {
  router.afterEach(to => {
    const appStore = useAppStore();
    const { i18nKey, title } = to.meta;

    const pageTitle = i18nKey ? $t(i18nKey) : title;

    const documentTitle = appStore.systemName ? `${pageTitle} - ${appStore.systemName}` : pageTitle;

    useTitle(documentTitle);
  });
}
