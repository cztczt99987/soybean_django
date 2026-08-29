"""
watchmigrate — 开发环境下监听模型变更，自动执行 makemigrations + migrate。

用法:
    python manage.py watchmigrate
    python manage.py watchmigrate --interval 1
    python manage.py watchmigrate --app api --app another_app

注意:
    * 仅用于开发环境; 生产环境不要运行。
    * 仍会生成标准的 migrations/000x_xxx.py 文件, 请照常提交到 Git。
    * 只是把"手动敲 makemigrations + migrate"变成"保存 models.py 自动执行",
      不绕过 Django 的迁移审查流程。
"""
from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand, CommandError, call_command
from django.db import DEFAULT_DB_ALIAS, connections


class Command(BaseCommand):
    help = "监听 models.py / models/*.py 变更, 自动执行 makemigrations + migrate (开发环境用)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=float,
            default=2.0,
            help="轮询文件改动的间隔秒数 (默认 2.0)",
        )
        parser.add_argument(
            "--app",
            dest="apps",
            action="append",
            default=[],
            help="只监听指定 app, 可多次传入 (默认: 全部 INSTALLED_APPS)",
        )
        parser.add_argument(
            "--noinput",
            action="store_true",
            dest="no_input",
            help="makemigrations 的非交互模式 (遇到新增字段无默认值时直接退出)",
        )
        parser.add_argument(
            "--migrate-db",
            dest="migrate_db",
            default=DEFAULT_DB_ALIAS,
            help=f"migrate 作用的数据库别名 (默认 {DEFAULT_DB_ALIAS})",
        )
        parser.add_argument(
            "--once",
            action="store_true",
            help="只跑一次 makemigrations + migrate, 然后退出 (不进入监听循环)",
        )

    # ------------------------------------------------------------------
    def handle(self, *args, **options):
        self.interval = max(0.3, float(options["interval"]))
        self.target_apps: list[str] = list(options["apps"]) or []
        self.no_input = bool(options["no_input"])
        self.migrate_db = options["migrate_db"]
        self.run_once = bool(options["once"])
        self.verbosity = int(options.get("verbosity", 1))

        if not settings.DEBUG:
            # 生产环境禁止, 防止误操作
            raise CommandError("DEBUG=False (生产环境), 不允许运行 watchmigrate。")

        self.watch_files = self._collect_watch_files()
        if not self.watch_files:
            self.stderr.write("未找到任何需要监听的 models 文件。")
            return

        self.stdout.write("==> watchmigrate 已启动 (Ctrl+C 退出)")
        self.stdout.write("    监听文件:")
        for f in sorted(self.watch_files):
            try:
                rel = os.path.relpath(str(f), str(settings.BASE_DIR))
            except ValueError:
                rel = str(f)
            self.stdout.write(f"      - {rel}")
        self.stdout.write(f"    轮询间隔: {self.interval}s")
        self.stdout.write("")

        # 优雅退出
        def _handler(signum, frame):
            self.stdout.write("")
            self.stdout.write("==> watchmigrate 已停止。再见！")
            sys.exit(0)

        signal.signal(signal.SIGINT, _handler)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, _handler)

        # 先跑一次
        self._run_makemigrations_and_migrate(first_run=True)
        if self.run_once:
            return

        snapshot = self._take_snapshot()
        while True:
            time.sleep(self.interval)
            current = self._take_snapshot()
            changed = [p for p in self.watch_files if snapshot.get(p) != current.get(p)]
            if changed:
                self.stdout.write("")
                self.stdout.write("------------------------------------------------------------")
                self.stdout.write(f"检测到 {len(changed)} 个 models 文件变更:")
                for p in changed:
                    try:
                        rel = os.path.relpath(str(p), str(settings.BASE_DIR))
                    except ValueError:
                        rel = str(p)
                    self.stdout.write(f"  M {rel}")
                self.stdout.write("------------------------------------------------------------")
                try:
                    self._run_makemigrations_and_migrate(first_run=False)
                except Exception as exc:  # noqa: BLE001
                    # 不中断监听, 修正代码后下次还能继续触发
                    self.stderr.write(f"[warn] 自动迁移失败: {exc}")
                snapshot = current
            # 每次循环结束做一次连接安全清理, 防止长连接漂移
            try:
                connections.close_all()
            except Exception:
                pass

    # ------------------------------------------------------------------
    def _collect_watch_files(self) -> list[Path]:
        files: list[Path] = []
        base_dir = Path(settings.BASE_DIR).resolve()
        if self.target_apps:
            app_configs = []
            for label in self.target_apps:
                try:
                    app_configs.append(apps.get_app_config(label))
                except LookupError as exc:
                    raise CommandError(str(exc)) from exc
        else:
            app_configs = list(apps.get_app_configs())

        for ac in app_configs:
            if not ac.path:
                continue
            app_path = Path(ac.path).resolve()
            # 只监听项目本地的业务 app (路径在 BASE_DIR 下), 跳过 site-packages 里的 Django 自带 app.
            # 一来它们 models 不会变, 二来 Windows 跨盘时 os.path.relpath 会报错.
            try:
                app_path.relative_to(base_dir)
            except ValueError:
                continue
            # models.py (单文件)
            mp = app_path / "models.py"
            if mp.is_file():
                files.append(mp)
            # models/ 包 (多文件)
            mpkg = app_path / "models"
            if mpkg.is_dir():
                for sub in mpkg.rglob("*.py"):
                    if sub.name.startswith("_") and sub.name != "__init__.py":
                        continue
                    files.append(sub.resolve())
        # 去重
        return sorted(set(files))

    def _take_snapshot(self) -> dict[Path, float]:
        snap: dict[Path, float] = {}
        for p in self.watch_files:
            try:
                snap[p] = p.stat().st_mtime_ns
            except OSError:
                snap[p] = 0.0
        return snap

    # ------------------------------------------------------------------
    def _run_makemigrations_and_migrate(self, *, first_run: bool) -> None:
        # 1. makemigrations
        make_args: list = []
        if self.target_apps:
            make_args.extend(self.target_apps)
        make_kwargs: dict = {
            "verbosity": max(0, int(self.verbosity) - 1),
            "interactive": (not self.no_input),
            "dry_run": False,
            "merge": False,
            "check_changes": False,
        }
        self.stdout.write(f"[{self._now()}] >>> makemigrations {' '.join(make_args) if make_args else ''}")
        try:
            # makemigrations 如果检测到变化, 会把输出 stdout/stderr 直接打印出来, 不额外捕获取
            before = self._count_migration_files()
            call_command("makemigrations", *make_args, **make_kwargs)
            after = self._count_migration_files()
            has_new = after > before
        except SystemExit:
            # makemigrations 内部会在"没有变更"或"成功"后不抛异常, 仅在无法交互时可能 sys.exit
            has_new = False
        except BaseException as exc:
            self.stderr.write(f"[makemigrations] 出错: {exc}")
            return

        # 2. migrate
        migrate_kwargs = {
            "verbosity": max(0, int(self.verbosity) - 1),
            "interactive": False,
            "database": self.migrate_db,
            "run_syncdb": False,
        }
        if first_run or has_new:
            self.stdout.write(f"[{self._now()}] >>> migrate --database {self.migrate_db}")
            try:
                call_command("migrate", **migrate_kwargs)
            except BaseException as exc:
                self.stderr.write(f"[migrate] 出错: {exc}")
                return
            self.stdout.write(f"[{self._now()}] [OK] 迁移完成。")
        else:
            # 没有新迁移, 仍轻量跑一下 migrate 以保证 django_migrations 表存在/对齐
            try:
                call_command("migrate", **{**migrate_kwargs, "verbosity": 0})
            except BaseException:
                pass

    # ------------------------------------------------------------------
    @staticmethod
    def _count_migration_files() -> int:
        total = 0
        for ac in apps.get_app_configs():
            if not ac.path:
                continue
            md = Path(ac.path) / "migrations"
            if not md.is_dir():
                continue
            total += sum(1 for f in md.glob("*.py") if not f.name.startswith("_"))
        return total

    @staticmethod
    def _now() -> str:
        return time.strftime("%H:%M:%S")
