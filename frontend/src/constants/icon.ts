/**
 * Icon picker data
 *
 * Curated iconify (mdi) icon names grouped by semantic category.
 * Icons are rendered on demand via @iconify/vue.
 */
export interface IconCategory {
  /** category key, maps to i18n `common.iconPicker.categories.${key}` */
  key: string;
  i18nKey: App.I18n.I18nKey;
  icons: string[];
}

export const iconPickerCategories: IconCategory[] = [
  {
    key: 'common',
    i18nKey: 'common.iconPicker.categories.common',
    icons: [
      'mdi:home',
      'mdi:home-outline',
      'mdi:magnify',
      'mdi:cog',
      'mdi:apps',
      'mdi:menu',
      'mdi:menu-open',
      'mdi:view-dashboard',
      'mdi:view-dashboard-outline',
      'mdi:palette',
      'mdi:theme-light-dark',
      'mdi:star',
      'mdi:star-outline',
      'mdi:heart',
      'mdi:information',
      'mdi:alert',
      'mdi:help-circle',
      'mdi:refresh',
      'mdi:earth',
      'mdi:tune-vertical'
    ]
  },
  {
    key: 'system',
    i18nKey: 'common.iconPicker.categories.system',
    icons: [
      'mdi:account-group',
      'mdi:shield-account',
      'mdi:shield-lock',
      'mdi:office-building',
      'mdi:sitemap',
      'mdi:book-open-variant',
      'mdi:book-open-outline',
      'mdi:clipboard-list',
      'mdi:database',
      'mdi:server',
      'mdi:lan',
      'mdi:history',
      'mdi:key',
      'mdi:key-chain',
      'mdi:lock',
      'mdi:lock-open',
      'mdi:certificate',
      'mdi:domain',
      'mdi:tools',
      'mdi:monitor-shimmer'
    ]
  },
  {
    key: 'user',
    i18nKey: 'common.iconPicker.categories.user',
    icons: [
      'mdi:account',
      'mdi:account-outline',
      'mdi:account-circle',
      'mdi:account-multiple',
      'mdi:account-plus',
      'mdi:account-edit',
      'mdi:account-remove',
      'mdi:account-search',
      'mdi:account-settings',
      'mdi:account-box',
      'mdi:account-box-outline',
      'mdi:account-group-outline',
      'mdi:face-man',
      'mdi:face-woman',
      'mdi:card-account-details'
    ]
  },
  {
    key: 'file',
    i18nKey: 'common.iconPicker.categories.file',
    icons: [
      'mdi:file',
      'mdi:file-outline',
      'mdi:file-document',
      'mdi:file-document-outline',
      'mdi:file-multiple',
      'mdi:file-pdf',
      'mdi:file-excel',
      'mdi:file-word',
      'mdi:file-image',
      'mdi:folder',
      'mdi:folder-outline',
      'mdi:folder-open',
      'mdi:download',
      'mdi:upload',
      'mdi:content-save',
      'mdi:content-save-outline',
      'mdi:content-copy',
      'mdi:clipboard-text',
      'mdi:printer'
    ]
  },
  {
    key: 'edit',
    i18nKey: 'common.iconPicker.categories.edit',
    icons: [
      'mdi:pencil',
      'mdi:pencil-outline',
      'mdi:pencil-box',
      'mdi:delete',
      'mdi:delete-outline',
      'mdi:delete-forever',
      'mdi:plus',
      'mdi:plus-box',
      'mdi:minus',
      'mdi:close',
      'mdi:check',
      'mdi:check-circle',
      'mdi:close-circle',
      'mdi:undo',
      'mdi:redo',
      'mdi:filter',
      'mdi:filter-outline',
      'mdi:sort',
      'mdi:tag',
      'mdi:tag-outline'
    ]
  },
  {
    key: 'chart',
    i18nKey: 'common.iconPicker.categories.chart',
    icons: [
      'mdi:chart-bar',
      'mdi:chart-line',
      'mdi:chart-pie',
      'mdi:chart-areaspline',
      'mdi:chart-donut',
      'mdi:chart-bubble',
      'mdi:chart-scatter-plot',
      'mdi:chart-histogram',
      'mdi:chart-timeline-variant',
      'mdi:finance',
      'mdi:trending-up',
      'mdi:trending-down',
      'mdi:poll',
      'mdi:monitor-dashboard',
      'mdi:gauge',
      'mdi:counter'
    ]
  },
  {
    key: 'message',
    i18nKey: 'common.iconPicker.categories.message',
    icons: [
      'mdi:email',
      'mdi:email-outline',
      'mdi:email-open',
      'mdi:message',
      'mdi:message-outline',
      'mdi:message-text',
      'mdi:message-processing',
      'mdi:bell',
      'mdi:bell-outline',
      'mdi:bell-ring',
      'mdi:phone',
      'mdi:send',
      'mdi:comment',
      'mdi:comment-text',
      'mdi:wechat',
      'mdi:qqchat',
      'mdi:github'
    ]
  },
  {
    key: 'navigate',
    i18nKey: 'common.iconPicker.categories.navigate',
    icons: [
      'mdi:arrow-left',
      'mdi:arrow-right',
      'mdi:arrow-up',
      'mdi:arrow-down',
      'mdi:chevron-left',
      'mdi:chevron-right',
      'mdi:chevron-up',
      'mdi:chevron-down',
      'mdi:chevron-double-left',
      'mdi:chevron-double-right',
      'mdi:logout',
      'mdi:login',
      'mdi:exit-to-app',
      'mdi:open-in-new',
      'mdi:link',
      'mdi:link-variant',
      'mdi:compass',
      'mdi:map-marker',
      'mdi:navigation',
      'mdi:dots-vertical',
      'mdi:dots-horizontal'
    ]
  }
];
