#!/usr/bin/env python
"""
一键启动 soybean_django 前后端开发环境

在 Trae 终端或命令行里直接执行:
    python start.py

按 Ctrl+C 可同时停止前后端进程。
"""
from __future__ import annotations

import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
LOG_DIR = ROOT / "logs"
BACKEND_LOG = LOG_DIR / "backend.log"
BACKEND_ERR = LOG_DIR / "backend.err.log"
DJANGO_PORT = 8000
VITE_PORT = 5173


def _ok(msg: str) -> None:
    print("    OK   " + msg)


def _warn(msg: str) -> None:
    print("    WARN " + msg)


def _err(msg: str) -> None:
    print("", file=sys.stderr)
    print("    FAIL: " + msg, file=sys.stderr)


def _title(msg: str) -> None:
    print()
    print("==> " + msg)


# ---------------------------------------------------------------------------
# 1. 检查命令是否存在
# ---------------------------------------------------------------------------
def check_cmd(name: str, hint: str = "") -> None:
    path = shutil.which(name)
    if not path:
        tail = f" {hint}" if hint else ""
        _err(f"未找到命令 `{name}`，请先安装并加入 PATH。{tail}")
        sys.exit(1)
    try:
        out = subprocess.check_output(
            [path, "--version"], stderr=subprocess.STDOUT, text=True
        )
        ver = out.splitlines()[0].strip()
    except Exception:
        ver = "(ok)"
    _ok(f"{name} {ver}")


def pnpm_exe() -> str:
    """解析 pnpm 真实可执行文件路径。

    Windows 上 pnpm 通常是 pnpm.cmd 批处理, 直接把 "pnpm" 传给
    subprocess 会因不按 PATHEXT 解析而报 WinError 2。
    """
    path = shutil.which("pnpm")
    if not path:
        _err("未找到 pnpm，请先安装: npm i -g pnpm")
        sys.exit(1)
    return path


# ---------------------------------------------------------------------------
# 2. 检查端口是否被占用
# ---------------------------------------------------------------------------
def check_port(port: int, name: str) -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        try:
            s.bind(("0.0.0.0", port))
        except OSError:
            _err(f"端口 {port} ({name}) 已被占用，请先释放该端口后重试。")
            sys.exit(1)
    finally:
        s.close()
    _ok(f"端口 {port} ({name}) 空闲")


# ---------------------------------------------------------------------------
# 3. 清理钩子
# ---------------------------------------------------------------------------
_procs: list[subprocess.Popen] = []
_log_handles: list = []


def _cleanup(signum=None, frame=None) -> None:
    print()
    print(">>> 正在停止前后端进程...")
    for p in _procs:
        if not p or p.poll() is not None:
            continue
        try:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    pass
            print(f"    - 已停止 PID#{p.pid}")
        except Exception as e:
            print(f"    - 停止 PID#{p.pid} 失败: {e}")
    for h in _log_handles:
        try:
            h.close()
        except Exception:
            pass
    print(">>> 全部已停止，再见！")
    sys.exit(0)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main() -> None:
    # 步骤 1: 环境检查
    _title("[1/6] 检查运行环境")
    check_cmd("python")
    check_cmd("node", "请安装 Node.js >= 20.19 并加入 PATH。")
    check_cmd("pnpm", "请安装 pnpm: npm i -g pnpm")

    # 步骤 2: 端口检查
    _title("[2/6] 检查端口占用")
    check_port(DJANGO_PORT, "Django")
    check_port(VITE_PORT, "Vite")

    # 步骤 3: 前端依赖
    _title("[3/6] 检查前端依赖")
    node_modules = FRONTEND_DIR / "node_modules"
    pnpm_ok = (node_modules / ".pnpm").exists()
    vite_ok = (node_modules / "vite").exists()
    if not (pnpm_ok and vite_ok):
        if node_modules.exists():
            _warn("node_modules 不完整（缺 vite 等），先删除残留后重新安装 ...")
            shutil.rmtree(node_modules, ignore_errors=True)
        _warn("开始执行 pnpm install ...")
        code = subprocess.call([pnpm_exe(), "install"], cwd=str(FRONTEND_DIR))
        if code != 0:
            _err(f"pnpm install 失败，退出码 {code}")
            sys.exit(1)
        _ok("前端依赖安装完成")
    else:
        _ok("前端依赖已就绪 (node_modules 完整)")

    # 步骤 4: 同步数据库结构（自动 makemigrations + migrate 一次）
    _title("[4/6] 同步数据库结构 (watchmigrate)")
    code = subprocess.call(
        [sys.executable, "manage.py", "watchmigrate", "--once", "--noinput"],
        cwd=str(BACKEND_DIR),
    )
    if code != 0:
        _err(f"watchmigrate 失败，退出码 {code}；请检查模型定义或数据库配置 (backend/.env)。")
        sys.exit(1)

    # 步骤 5: 启动 Django
    _title(f"[5/6] 启动 Django 后端 (端口 {DJANGO_PORT})")
    LOG_DIR.mkdir(exist_ok=True)
    if BACKEND_LOG.exists():
        BACKEND_LOG.unlink()
    if BACKEND_ERR.exists():
        BACKEND_ERR.unlink()

    signal.signal(signal.SIGINT, _cleanup)
    signal.signal(signal.SIGTERM, _cleanup)

    log_f = open(BACKEND_LOG, "ab")
    err_f = open(BACKEND_ERR, "ab")
    _log_handles.extend([log_f, err_f])

    django = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"0.0.0.0:{DJANGO_PORT}", "--noreload"],
        cwd=str(BACKEND_DIR),
        stdout=log_f,
        stderr=err_f,
    )
    _procs.append(django)
    print(f"    后端日志: {BACKEND_LOG}")
    print(f"    错误日志: {BACKEND_ERR}")

    started = False
    for _ in range(20):
        time.sleep(0.5)
        if django.poll() is not None:
            _err("后端进程已退出")
            print("     --- backend.err.log ---")
            if BACKEND_ERR.exists():
                text = BACKEND_ERR.read_text(encoding="utf-8", errors="replace")
                for line in text.splitlines():
                    print("     " + line)
            print("     --- backend.log ---")
            if BACKEND_LOG.exists():
                text = BACKEND_LOG.read_text(encoding="utf-8", errors="replace")
                for line in text.splitlines():
                    print("     " + line)
            _cleanup()
        if BACKEND_LOG.exists():
            txt = BACKEND_LOG.read_text(encoding="utf-8", errors="replace")
            if "Starting development server" in txt or "Django version" in txt:
                started = True
                break
    if started:
        _ok(f"Django 已启动 (PID#{django.pid})")
    else:
        _warn("未检测到 Django 启动完成消息，但进程仍存活，请稍后查看后端日志确认")

    # 步骤 6: 启动前端（前台阻塞）
    _title(f"[6/6] 启动前端 Vite (端口 {VITE_PORT})")
    print()
    print("===========================================================")
    print(f"  Django API : http://localhost:{DJANGO_PORT}")
    print(f"  API 健康   : http://localhost:{DJANGO_PORT}/api/health")
    print(f"  前端地址   : http://localhost:{VITE_PORT}")
    print()
    print("  前端代理 /proxy-default 当前指向 apifox mock")
    print("  如需对接本地 Django，修改 frontend/.env.test:")
    print(f"    VITE_SERVICE_BASE_URL=http://localhost:{DJANGO_PORT}")
    print()
    print("  按 Ctrl+C 将同时停止前后端进程并退出")
    print("===========================================================")
    print()

    vite = subprocess.Popen([pnpm_exe(), "dev"], cwd=str(FRONTEND_DIR))
    _procs.append(vite)
    try:
        vite.wait()
    finally:
        _cleanup()


if __name__ == "__main__":
    main()
