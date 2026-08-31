# soybean_django 后台管理底座

开箱即用的后台管理系统底座，可直接作为新项目的起点。

- 前端：[SoybeanAdmin](https://github.com/soybeanjs/soybean-admin)（Vue 3 + Vite + Naive UI + UnoCSS + Pinia）
- 后端：Django 5.1 + Django REST Framework + drf-spectacular（Swagger 文档）
- 数据库：PostgreSQL / MySQL / SQLite（通过 `.env` 的 `DB_ENGINE` 切换）
- 缓存：Redis（可选，`REDIS_URL` 未配置时自动退化为本地内存缓存）
- 内置功能：用户 / 角色 / 菜单（按钮级权限）/ 部门 / 岗位 / 字典 / 参数设置 / 操作日志 / 服务器与缓存监控 / 存储配置 / 定时任务调度 / API 文档管理

接口文档（启动后端后访问）：

- Swagger UI: <http://localhost:8000/api/docs/>
- OpenAPI Schema: <http://localhost:8000/api/schema/>

## 快速开始

### 1. 后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 复制环境变量并按需修改（数据库 / Redis）
cp .env.example .env

# 同步数据库结构
python manage.py migrate

# 初始化种子数据（部门 / 角色 / 菜单 / 字典 / 参数 / 默认账号）
python manage.py seed_system

# 启动（默认 http://localhost:8000）
python manage.py runserver
```

### 2. 前端

```bash
cd frontend
pnpm install
pnpm dev          # 默认 http://localhost:9527，代理指向 backend/.env.test 中的 VITE_SERVICE_BASE_URL
```

### 3. 默认账号

| 账号  | 密码       | 说明                          |
| ----- | ---------- | ----------------------------- |
| admin | admin123   | 超级管理员，全部权限          |
| demo  | admin123   | 演示用户，仅只读部分模块      |

登录需填写图形验证码（20 以内加减法，5 分钟有效、一次性使用）；后端重启后旧验证码失效，刷新图片重填即可。

### 4. 一键启动（可选）

仓库根目录提供 `start.py`，同时拉起前后端并自动同步数据库结构：

```bash
python start.py
```

## 基于底座创建新项目

底座保持冻结（当前版本见 tag `v1.0.0-base`），新项目从它初始化为独立仓库：

```bash
# 1. 克隆底座到新目录
git clone https://github.com/cztczt99987/soybean_django.git my-new-project
cd my-new-project

# 2. 断开底座 remote，指向新项目自己的空仓库
git remote remove origin
git remote add origin <新项目仓库地址>
git push -u origin main
```

如需跟进底座后续修复，可在新项目中保留一条升级通道：

```bash
git remote add base https://github.com/cztczt99987/soybean_django.git
git fetch base
git merge base/main        # 整体合并底座更新，或用 cherry-pick 挑选提交
```

## 目录结构

```
backend/            Django 后端
  api/              业务应用
    models/         rbac(用户/角色/菜单...) system(字典/参数/日志) tasks(定时任务)
    views/          auth(鉴权) system(系统管理) monitor(监控) task(任务)
    serializers/    与 views 同构拆分
    scheduler.py    APScheduler 调度器封装
  config/           Django 工程配置
frontend/           SoybeanAdmin 前端
  src/views/        页面（动态路由由后端菜单驱动，VITE_AUTH_ROUTE_MODE=dynamic）
docs/               补充文档（task-usage / 后端代码结构说明）
start.py            前后端一键启动脚本
```
