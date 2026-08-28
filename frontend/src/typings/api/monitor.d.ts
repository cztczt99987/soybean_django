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
    }

    interface CacheSearchParams {
      keyword?: string | null;
    }

    interface CacheListResp {
      mode: 'redis' | 'locmem';
      total: number;
      records: CacheRow[];
      serverInfo: {
        redisVersion?: string;
        usedMemory?: number;
        usedMemoryHuman?: string;
        maxMemoryHuman?: string;
        connectedClients?: number;
        dbSize?: number;
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
