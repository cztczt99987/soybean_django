/** 任务管理模块类型: 定时任务 / 执行日志 / 执行节点 / 调度器监控 */
declare namespace Api {
  namespace Task {
    type ListResp<T> = Api.Common.PaginatingQueryRecord<T>;

    /** 基础行字段 (与后端 BaseModel 对齐) */
    interface BaseRow {
      id: number;
      remark?: string;
      sort_order?: number;
      created_at?: string;
      updated_at?: string;
    }

    type TaskStatus = '1' | '0';
    type TaskPriority = '1' | '2' | '3';
    type TriggerType = 'cron' | 'interval' | 'date';
    type JobType = 'function' | 'http';
    type ExecStatus = 'running' | 'success' | 'failed' | 'timeout';
    type SchedulerState = 'running' | 'paused' | 'stopped';

    /** 定时任务 */
    interface TaskJob extends BaseRow {
      name: string;
      description: string;
      job_type: JobType;
      handler: string;
      http_method: string;
      http_url: string;
      http_body: string;
      trigger_type: TriggerType;
      cron_expr: string;
      interval_seconds: number;
      run_date?: string | null;
      priority: TaskPriority;
      timeout_seconds: number;
      status: TaskStatus;
      next_run_at?: string | null;
      last_run_at?: string | null;
      last_status?: ExecStatus | '';
      /** 触发规则人性化描述 (后端计算) */
      triggerDesc?: string;
      /** 是否已注册到调度器 (后端计算) */
      isRunning?: boolean;
    }

    interface TaskJobSearchParams extends Api.Common.CommonSearchParams {
      name?: string | null;
      status?: TaskStatus | null;
      trigger_type?: TriggerType | null;
    }

    /** 任务执行历史 */
    interface ExecutionLog extends BaseRow {
      job: number;
      job_name: string;
      node_name: string;
      status: ExecStatus;
      trigger: string;
      started_at: string;
      finished_at?: string | null;
      duration_ms: number;
      output?: string;
      error_msg?: string;
    }

    interface LogSearchParams extends Api.Common.CommonSearchParams {
      job?: number;
      status?: ExecStatus | null;
      job_name?: string | null;
    }

    /** 执行节点 */
    interface SchedulerNode extends BaseRow {
      name: string;
      node_id: string;
      host: string;
      port: number;
      isLocal: boolean;
      status: TaskStatus;
      max_concurrency: number;
      current_load: number;
      version: string;
      heartbeat_at?: string | null;
      /** 是否在线 (后端根据心跳计算) */
      isOnline: boolean;
    }

    interface NodeSearchParams extends Api.Common.CommonSearchParams {
      name?: string | null;
      status?: TaskStatus | null;
    }

    /** 调度器监控指标 */
    interface SchedulerStatus {
      state: SchedulerState;
      startedAt: number | null;
      uptime: number;
      jobCount: number;
      enabledJobCount: number;
      scheduledJobCount: number;
      runningCount: number;
      nodeOnlineCount: number;
      nodeCount: number;
      process: { cpuPercent: number; memPercent: number };
      metrics: {
        total: number;
        success: number;
        failed: number;
        timeout: number;
        todayTotal: number;
        todaySuccess: number;
        todayFailed: number;
        successRate: number;
        avgDurationMs: number;
      };
      alerts: {
        id: number;
        jobName: string;
        status: string;
        error: string;
        startedAt: string;
        nodeName: string;
      }[];
      nextJobs: { id: number; name: string; triggerType: string; nextRunAt: string | null }[];
    }

    /** 调度器控制台日志 */
    interface ConsoleLog {
      time: string;
      level: string;
      msg: string;
    }
  }
}
