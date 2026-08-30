"""独立进程运行任务调度器。

用法:
    python manage.py runscheduler

用于不依赖 runserver 的部署方式 (如 gunicorn 部署 Web + 独立调度进程),
Ctrl+C 优雅退出。
"""

from __future__ import annotations

import time

from django.core.management import BaseCommand

from api.scheduler import scheduler_engine


class Command(BaseCommand):
    help = "独立进程运行任务调度器 (Ctrl+C 退出)"

    def handle(self, *args, **options):
        scheduler_engine.register_local_node()
        scheduler_engine.start()
        count = scheduler_engine.reload_jobs()
        self.stdout.write(self.style.SUCCESS(f"调度器已启动, 装载任务 {count} 个 (Ctrl+C 退出)"))
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("正在停止调度器...")
            scheduler_engine.shutdown()
            self.stdout.write(self.style.SUCCESS("调度器已停止"))
