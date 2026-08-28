"""监控模块接口真实 HTTP 测试：功能 / 参数校验 / 兼容性 / 性能。

用法: python _test_monitor_api.py [port]
需先在目标端口启动 Django。
"""
from __future__ import annotations

import json
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
BASE = f"http://127.0.0.1:{PORT}/api"

PASS, FAIL = 0, 0
failures: list[str] = []


def call(method, path, token=None, data=None, params=None, timeout=30):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", errors="replace")
            try:
                return r.status, json.loads(raw)
            except json.JSONDecodeError:
                return r.status, {"raw": raw[:200]}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"raw": raw[:200]}


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        failures.append(f"{name} {detail}")
        print(f"  [FAIL] {name} {detail}")


def wait_ready(timeout=90):
    end = time.time() + timeout
    while time.time() < end:
        try:
            s, b = call("GET", "/health")
            if s == 200 and b.get("code") == "0000":
                return True
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1)
    return False


def main():
    print("=" * 62)
    print(f"监控管理接口测试  target={BASE}")
    print("=" * 62)

    if not wait_ready():
        print("!! Django 未就绪，请先在该端口启动 runserver")
        return 2

    # 登录
    s, b = call("POST", "/auth/login", data={"userName": "admin", "password": "admin123"})
    assert s == 200 and b.get("code") == "0000", b
    token = b["data"]["token"]
    print(f"登录成功 token={token[:10]}...\n")

    # ---------- 1. 功能测试 ----------
    print("[1] 功能测试")
    s, b = call("GET", "/monitor/server", token=token)
    d = b.get("data") or {}
    check("服务器信息 200/0000", s == 200 and b.get("code") == "0000", str(b)[:120])
    check("含 os/cpu/memory/disks/network 五段", all(k in d for k in ("os", "cpu", "memory", "disks", "network")))
    check("cpu 使用率为数值", isinstance(d.get("cpu", {}).get("percent"), (int, float)))
    check("内存总量 > 0", d.get("memory", {}).get("total", 0) > 0)
    check("磁盘列表非空", len(d.get("disks") or []) > 0)
    check("网络 IP 非空", bool(d.get("network", {}).get("ip")))

    s, b = call("GET", "/monitor/cache", token=token)
    d = b.get("data") or {}
    check("缓存列表 200/0000", s == 200 and b.get("code") == "0000", str(b)[:120])
    check("mode 为 redis/locmem", d.get("mode") in ("redis", "locmem"), str(d.get("mode")))
    check("records 为列表", isinstance(d.get("records"), list))
    cache_mode = d.get("mode")

    s, b = call("GET", "/monitor/files", token=token)
    d = b.get("data") or {}
    check("文件列表 200/0000", s == 200 and b.get("code") == "0000", str(b)[:120])
    check("含 currentPath/entries/disk", all(k in d for k in ("currentPath", "entries", "disk")))
    check("entries 含 name/isDir/size/modified", all(
        {"name", "isDir", "size", "modified"} <= set(e) for e in (d.get("entries") or [])[:5]))
    first_dir = next((e["path"] for e in (d.get("entries") or []) if e["isDir"]), None)

    if first_dir:
        s, b = call("GET", "/monitor/files", token=token, params={"path": first_dir})
        check(f"子目录进入 {first_dir}", s == 200 and b.get("code") == "0000", str(b)[:120])

    s, b = call("GET", "/monitor/storage", token=token, params={"type": "local"})
    d = b.get("data") or {}
    check("存储配置读取", s == 200 and b.get("code") == "0000" and "active" in d, str(b)[:120])

    # 写入 -> 验证 -> 读取回显 -> 切换
    s, b = call("POST", "/monitor/storage", token=token,
                data={"type": "local", "config": {"basePath": "d:/work/soybean_django"}, "validate": True})
    check("存储配置验证通过", s == 200 and b.get("code") == "0000", str(b)[:120])

    s, b = call("POST", "/monitor/storage", token=token,
                data={"type": "local", "config": {"basePath": "d:/work/soybean_django"}})
    check("存储配置保存", s == 200 and b.get("code") == "0000", str(b)[:120])

    s, b = call("GET", "/monitor/storage", token=token, params={"type": "local"})
    check("保存后回显一致", (b.get("data") or {}).get("config", {}).get("basePath") == "d:/work/soybean_django",
          str(b.get("data"))[:120])

    s, b = call("POST", "/monitor/storage", token=token, data={"active": "local"})
    check("切换激活存储", s == 200 and b.get("code") == "0000", str(b)[:120])

    # 缓存删除（仅 redis 模式实际删）
    if cache_mode == "redis":
        s, b = call("POST", "/monitor/cache/delete", token=token, data={"key": "nonexistent_key_xyz"})
        check("缓存单删(不存在的键)", s == 200 and b.get("code") == "0000", str(b)[:120])
    else:
        s, b = call("POST", "/monitor/cache/delete", token=token, data={"key": "x"})
        check("locmem 模式删除返回业务错误", b.get("code") != "0000", str(b)[:120])

    # ---------- 2. 请求参数验证 ----------
    print("\n[2] 请求参数验证")
    s, b = call("POST", "/monitor/storage", token=token, data={"type": "aliyun", "config": {}})
    check("云存储缺必填被拦截", b.get("code") != "0000" and "endpoint" in str(b.get("msg")), str(b)[:140])

    s, b = call("POST", "/monitor/storage", token=token, data={"type": "notexist", "config": {}})
    check("非法存储类型被拦截", b.get("code") != "0000", str(b)[:120])

    s, b = call("GET", "/monitor/storage", token=token, params={"type": "bogus"})
    check("非法 type 查询被拦截", b.get("code") != "0000", str(b)[:120])

    s, b = call("POST", "/monitor/cache/delete", token=token, data={})
    check("缓存删除缺 key 被拦截", b.get("code") != "0000", str(b)[:120])

    s, b = call("GET", "/monitor/files", token=token, params={"path": "../../etc/passwd"})
    check("目录穿越被拦截", b.get("code") != "0000", str(b)[:120])

    s, b = call("GET", "/monitor/files", token=token, params={"path": ".."})
    check("上级越界被拦截", b.get("code") != "0000", str(b)[:120])

    s, b = call("GET", "/monitor/files", token=token, params={"path": "not_exist_dir_9x7"})
    check("不存在目录返回业务错误", b.get("code") != "0000", str(b)[:120])

    s, b = call("GET", "/monitor/file/download", token=token, params={"path": "."})
    check("下载目录(非文件)被拦截", b.get("code") != "0000", str(b)[:120])

    # ---------- 3. 兼容性测试 ----------
    print("\n[3] 兼容性 / 鉴权")
    s, b = call("GET", "/monitor/server")
    check("无 token -> 401 + code 1000", s == 401 and b.get("code") == "1000", f"status={s} body={str(b)[:100]}")

    s, b = call("GET", "/monitor/cache", token="invalid_token_abcdef")
    check("无效 token -> 401", s == 401 and b.get("code") == "1000", f"status={s}")

    s, b = call("POST", "/monitor/cache/delete")
    check("写操作无 token -> 401", s == 401, f"status={s}")

    s, b = call("GET", "/monitor/files", token=token, params={"path": ""})
    check("空 path 视为根目录", b.get("code") == "0000", str(b)[:120])

    s, b = call("GET", "/monitor/files", token=token, params={"path": "backend"})
    check("路径分隔符兼容(斜杠)", b.get("code") == "0000", str(b)[:120])

    s, b = call("GET", "/monitor/cache", token=token, params={"keyword": "django"})
    check("关键字含普通字符可查", b.get("code") == "0000", str(b)[:120])

    s, b = call("GET", "/monitor/cache", token=token, params={"keyword": "中文键名*?"})
    check("关键字含中文/通配符不报500", s == 200, f"status={s}")

    # ---------- 4. 性能测试 ----------
    print("\n[4] 性能测试（每项 10 次串行 + 10 并发）")

    def bench(name, fn, budget_ms):
        latents = []
        errs = 0
        for _ in range(10):
            t0 = time.perf_counter()
            st, bb = fn()
            latents.append((time.perf_counter() - t0) * 1000)
            if bb.get("code") != "0000":
                errs += 1
        avg = statistics.mean(latents)
        p95 = sorted(latents)[9]
        with ThreadPoolExecutor(max_workers=10) as ex:
            t0 = time.perf_counter()
            res = list(ex.map(lambda _: fn(), range(10)))
            wall = (time.perf_counter() - t0) * 1000
        conc_err = sum(1 for st, bb in res if bb.get("code") != "0000")
        ok_ = errs == 0 and conc_err == 0 and avg < budget_ms
        check(f"{name} avg={avg:.0f}ms p95={p95:.0f}ms 并发10耗时={wall:.0f}ms (预算{budget_ms}ms)", ok_,
              f"串行失败{errs} 并发失败{conc_err}")

    bench("服务器信息", lambda: call("GET", "/monitor/server", token=token), 2500)
    bench("缓存列表", lambda: call("GET", "/monitor/cache", token=token), 3000)
    bench("文件根目录", lambda: call("GET", "/monitor/files", token=token), 1500)
    bench("存储配置读", lambda: call("GET", "/monitor/storage", token=token, params={"type": "local"}), 800)

    # ---------- 5. 响应格式规范 ----------
    print("\n[5] 响应格式规范")
    s, b = call("GET", "/monitor/server", token=token)
    check("外层含 code/msg/data 三键", set(b.keys()) == {"code", "msg", "data"}, str(list(b.keys())))
    check("成功码为 '0000' 字符串", b.get("code") == "0000")
    s, b = call("GET", "/monitor/files", token=token, params={"path": "../x"})
    check("错误响应同为 code/msg/data 结构", set(b.keys()) == {"code", "msg", "data"} and b.get("code") != "0000")
    check("错误响应含中文可读 msg", bool(str(b.get("msg", "")).strip()), str(b)[:100])

    print("\n" + "=" * 62)
    print(f"结果: PASS={PASS}  FAIL={FAIL}")
    if failures:
        print("失败项:")
        for f in failures:
            print("  -", f)
    print("=" * 62)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
