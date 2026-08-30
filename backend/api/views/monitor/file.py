"""服务器文件目录浏览与下载视图。"""

from __future__ import annotations

import shutil
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.response import Response

from ...serializers.schemas import FileDownloadQuerySerializer, FileListQuerySerializer
from ..common import APIView, _log_operation, fail, ok, require_auth

# 文件浏览允许访问的根目录（项目根）
FILE_BROWSE_ROOT = Path(settings.BASE_DIR).parent.resolve()


def _safe_resolve(rel_path: str) -> Path:
    """把相对路径解析到 FILE_BROWSE_ROOT 内，防目录穿越。"""
    base = FILE_BROWSE_ROOT
    target = (base / (rel_path or ".")).resolve()
    if target != base and base not in target.parents:
        raise ValueError("非法路径")
    return target


class FileListView(APIView):
    """服务器目录列表。"""

    @extend_schema(
        parameters=[FileListQuerySerializer],
        responses={200: OpenApiResponse(description="返回 {currentPath, parentPath, entries, disk}")},
        summary="目录浏览",
    )
    @require_auth
    def get(self, request):
        rel = (request.query_params.get("path") or "").strip()
        try:
            target = _safe_resolve(rel)
        except ValueError:
            return Response(fail("非法路径"))

        if not target.exists() or not target.is_dir():
            return Response(fail("目录不存在"))

        entries = []
        for child in sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            try:
                st = child.stat()
                hidden = child.name.startswith(".")
                if child.is_dir():
                    # 目录不做递归统计（node_modules 等级联目录会极慢），size 固定 0，前端显示 '-'
                    entries.append(
                        {
                            "name": child.name,
                            "path": str(child.relative_to(FILE_BROWSE_ROOT)).replace("\\", "/"),
                            "isDir": True,
                            "size": 0,
                            "modified": int(st.st_mtime),
                            "hidden": hidden,
                        }
                    )
                else:
                    entries.append(
                        {
                            "name": child.name,
                            "path": str(child.relative_to(FILE_BROWSE_ROOT)).replace("\\", "/"),
                            "isDir": False,
                            "size": st.st_size,
                            "modified": int(st.st_mtime),
                            "hidden": hidden,
                        }
                    )
            except (PermissionError, OSError):
                continue

        usage = shutil.disk_usage(str(target))
        return Response(
            ok(
                {
                    "currentPath": str(target.relative_to(FILE_BROWSE_ROOT)).replace("\\", "/") or ".",
                    "parentPath": (
                        str(target.parent.relative_to(FILE_BROWSE_ROOT)).replace("\\", "/")
                        if target != FILE_BROWSE_ROOT
                        else None
                    ),
                    "entries": entries,
                    "disk": {"total": usage.total, "used": usage.used, "free": usage.free},
                }
            )
        )


class FileDownloadView(APIView):
    """下载单个文件。"""

    @extend_schema(
        parameters=[FileDownloadQuerySerializer],
        responses={200: OpenApiResponse(description="文件流（Content-Disposition 附件下载）")},
        summary="文件下载",
    )
    @require_auth
    def get(self, request):
        rel = (request.query_params.get("path") or "").strip()
        try:
            target = _safe_resolve(rel)
        except ValueError:
            return Response(fail("非法路径"))

        if not target.is_file():
            return Response(fail("文件不存在"))

        _log_operation(request, "文件管理", f"下载文件 {rel}", op_type="6")
        return FileResponse(target.open("rb"), as_attachment=True, filename=target.name)
