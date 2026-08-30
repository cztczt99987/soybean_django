/**
 * Namespace Api.Monitor
 *
 * 监控管理模块（服务器信息 / Redis 缓存 / 文件管理 / 存储配置）接口类型
 */
declare namespace Api {
  namespace Monitor {
    /** 服务器信息 */
    interface ServerInfo {
      os: {
        name: string;
        version: string;
        release: string;
        machine: string;
        processor: string;
        pythonVersion: string;
        djangoVersion: string;
        hostname: string;
        bootTime: number;
        uptime: number;
      };
      cpu: {
        physicalCores: number;
        logicalCores: number;
        percent: number;
        freqCurrent: number;
        freqMin: number;
        freqMax: number;
      };
      memory: {
        total: number;
        used: number;
        available: number;
        percent: number;
        swapTotal: number;
        swapUsed: number;
        swapPercent: number;
      };
      disks: Array<{
        device: string;
        mountpoint: string;
        fstype: string;
        total: number;
        used: number;
        free: number;
        percent: number;
      }>;
      diskRoot: { total: number; used: number; free: number; percent: number };
      network: {
        ip: string;
        bytesSent: number;
        bytesRecv: number;
        packetsSent: number;
        packetsRecv: number;
      };
      process: { pid: number; startedAt: number };
    }

    /** 缓存对象行 */
    interface CacheRow {
      key: string;
      type: string;
      size: number;
      /** 剩余过期秒数；-1 表示不过期 */
      ttl: number;
      /** 业务分类（剥离 Django 前缀/版本号后的首段） */
      category: string;
      /** 业务分类展示名 */
      categoryLabel: string;
    }

    /** 缓存分类汇总 */
    interface CacheCategorySummary {
      /** 分类名（原始段） */
      name: string;
      /** 展示名 */
      label: string;
      /** 键数量 */
      count: number;
      /** 总占用字节 */
      size: number;
    }

    /** 缓存键内容详情 */
    interface CacheDetailResp {
      key: string;
      type: string;
      /** 剩余过期秒数；-1 表示不过期 */
      ttl: number;
      /** 缓存内容（字符串化后） */
      value: string;
    }

    interface CacheSearchParams {
      keyword?: string | null;
    }

    interface CacheListResp {
      mode: 'redis' | 'locmem';
      total: number;
      records: CacheRow[];
      categories: CacheCategorySummary[];
      serverInfo: {
        redisVersion?: string;
        /** 运行模式：单机/集群 */
        runMode?: string;
        port?: number;
        connectedClients?: number;
        uptimeDays?: number;
        usedMemory?: number;
        usedMemoryHuman?: string;
        maxMemory?: number;
        maxMemoryHuman?: string;
        /** 瞬时 CPU 占用（单核百分比） */
        usedCpuPercent?: number;
        aofEnabled?: boolean;
        rdbStatus?: string;
        dbSize?: number;
        /** 瞬时网络 IO（KB/s） */
        netInKps?: number;
        netOutKps?: number;
        /** 命令统计：{ 命令名: 调用次数 } */
        commandStats?: Record<string, number>;
      };
    }

    /** 文件目录条目 */
    interface FileEntry {
      name: string;
      path: string;
      isDir: boolean;
      size: number;
      modified: number;
      hidden: boolean;
    }

    interface FileListResp {
      currentPath: string;
      parentPath: string | null;
      entries: FileEntry[];
      disk: { total: number; used: number; free: number };
    }

    /** 存储类型 */
    type StorageType = 'local' | 'aliyun' | 'tencent' | 'qiniu';

    interface StorageConfigResp {
      type: StorageType;
      config: Record<string, unknown>;
      active: StorageType;
    }
  }
}
