"""Swagger 文档测试。

覆盖范围:
1. OpenAPI Schema 生成: /api/schema/ 可生成且包含系统管理路径
2. Swagger UI 页面: /api/docs/ 可访问

约定: 所有接口返回 {code, msg, data}, 成功 code="0000"; 业务失败 code="5000"。
"""

from django.test import TestCase

from .tests import API


class SwaggerDocsTests(TestCase):
    """Swagger 文档集成。"""

    def test_openapi_schema_generatable(self):
        """输入: GET /api/schema/ (Accept: application/json)
        预期: HTTP 200, openapi 字段存在且包含 system 路径"""
        resp = self.client.get(f"{API}/schema/", HTTP_ACCEPT="application/json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("openapi", data)
        paths = data.get("paths", {})
        self.assertTrue(any(p.startswith("/api/system/user") for p in paths))

    def test_swagger_ui_page_accessible(self):
        """输入: GET /api/docs/
        预期: HTTP 200, 返回 HTML 页面"""
        resp = self.client.get(f"{API}/docs/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp["Content-Type"])

    def test_docs_schema_endpoint_served(self):
        """输入: GET /api/schema/ 携带 JSON Accept 头
        预期: 可访问 (Swagger UI 数据源)"""
        resp = self.client.get(f"{API}/schema/", HTTP_ACCEPT="application/json")
        self.assertEqual(resp.status_code, 200)
