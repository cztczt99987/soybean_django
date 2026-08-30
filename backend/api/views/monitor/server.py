"""服务器信息视图（只读）。"""

from __future__ import annotations

import os
import platform
import socket
import time
from pathlib import Path

from django.conf import settings
from rest_framework.response import Response

from ..common import APIView, ok, require_auth

BOOT_TIME = time.time()


class ServerInfoView(APIView):
    """服务器基础信息（只读）。"""

    @require_auth
    def get(self, request):
        import psutil  # noqa: PLC0415

        cpu_percent = psutil.cpu_percent(interval=0.3)
        cpu_freq = psutil.cpu_freq()
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        boot = psutil.boot_time()
        disk_root = psutil.disk_usage(str(Path(settings.BASE_DIR).drive or "/"))

        disks = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except OSError:
                continue
            disks.append(
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                }
            )

        net_io = psutil.net_io_counters()

        data = {
            "os": {
                "name": platform.system(),
                "version": platform.version(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor() or "N/A",
                "pythonVersion": platform.python_version(),
                "djangoVersion": __import__("django").get_version(),
                "hostname": socket.gethostname(),
                "bootTime": int(boot),
                "uptime": int(time.time() - boot),
            },
            "cpu": {
                "physicalCores": psutil.cpu_count(logical=False) or 0,
                "logicalCores": psutil.cpu_count(logical=True) or 0,
                "percent": cpu_percent,
                "freqCurrent": round(cpu_freq.current, 0) if cpu_freq else 0,
                "freqMin": round(cpu_freq.min, 0) if cpu_freq and cpu_freq.min else 0,
                "freqMax": round(cpu_freq.max, 0) if cpu_freq and cpu_freq.max else 0,
            },
            "memory": {
                "total": mem.total,
                "used": mem.used,
                "available": mem.available,
                "percent": mem.percent,
                "swapTotal": swap.total,
                "swapUsed": swap.used,
                "swapPercent": swap.percent,
            },
            "disks": disks,
            "diskRoot": {
                "total": disk_root.total,
                "used": disk_root.used,
                "free": disk_root.free,
                "percent": disk_root.percent,
            },
            "network": {
                "ip": _local_ip(),
                "bytesSent": net_io.bytes_sent,
                "bytesRecv": net_io.bytes_recv,
                "packetsSent": net_io.packets_sent,
                "packetsRecv": net_io.packets_recv,
            },
            "process": {
                "pid": os.getpid(),
                "startedAt": BOOT_TIME,
            },
        }
        return Response(ok(data))


def _local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"
