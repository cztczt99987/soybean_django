from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """runserver 时随进程启动任务调度器。

        - --noreload 模式 (dev.bat/start.py 使用): 直接启动
        - 自动重载模式: 仅在 RUN_MAIN=true 的子进程中启动, 避免双份调度
        """
        import os
        import sys

        if 'runserver' not in sys.argv:
            return
        if '--noreload' not in sys.argv and os.environ.get('RUN_MAIN') != 'true':
            return
        if '--help' in sys.argv or '--version' in sys.argv:
            return

        from . import scheduler

        # 延迟启动: 避免 ready() 阶段直接查询数据库触发 RuntimeWarning
        import threading

        def _start_engine():
            try:
                scheduler.scheduler_engine.register_local_node()
                scheduler.scheduler_engine.start()
            except Exception:  # noqa: BLE001  数据库未就绪 (如 migrate 阶段) 时不阻塞启动
                import logging

                logging.getLogger(__name__).warning("调度器启动失败 (可能数据库未就绪)", exc_info=True)

        threading.Timer(0.5, _start_engine).start()
