/** 任务管理模块常量: 触发方式 / 任务类型 / 优先级 / 执行状态 */

import { transformRecordToOption } from '@/utils/common';

export type TriggerType = 'cron' | 'interval' | 'date';
export type JobType = 'function' | 'http';
export type TaskPriority = '1' | '2' | '3';
export type ExecStatus = 'running' | 'success' | 'failed' | 'timeout';

export const triggerTypeRecord: Record<TriggerType, App.I18n.I18nKey> = {
  cron: 'page.task.job.triggerCron',
  interval: 'page.task.job.triggerInterval',
  date: 'page.task.job.triggerDate'
};

export const triggerTypeOptions = transformRecordToOption(triggerTypeRecord);

export const jobTypeRecord: Record<JobType, App.I18n.I18nKey> = {
  function: 'page.task.job.typeFunction',
  http: 'page.task.job.typeHttp'
};

export const jobTypeOptions = transformRecordToOption(jobTypeRecord);

export const taskPriorityRecord: Record<TaskPriority, App.I18n.I18nKey> = {
  '1': 'page.task.job.priorityHigh',
  '2': 'page.task.job.priorityMedium',
  '3': 'page.task.job.priorityLow'
};

export const taskPriorityOptions = transformRecordToOption(taskPriorityRecord);

/** 执行状态 → NTag 类型映射 */
export const execStatusTagType: Record<ExecStatus, NaiveUI.ThemeColor> = {
  running: 'info',
  success: 'success',
  failed: 'error',
  timeout: 'warning'
};
