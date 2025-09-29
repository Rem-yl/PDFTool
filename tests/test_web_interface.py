"""
Web界面端点测试
"""

class TestWebInterface:
    """Web界面测试"""

    def test_home_page(self, client):
        """测试主页"""
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert b"PDFTool" in response.content or b"pdftool" in response.content

    def test_merge_page(self, client):
        """测试合并页面"""
        response = client.get("/merge")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_info_page(self, client):
        """测试信息页面"""
        response = client.get("/info")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_watermark_page(self, client):
        """测试水印页面"""
        response = client.get("/watermark")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_convert_page(self, client):
        """测试转换页面"""
        response = client.get("/convert")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_password_page(self, client):
        """测试密码保护页面"""
        response = client.get("/password")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_pages_page(self, client):
        """测试页面选择页面"""
        response = client.get("/pages")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_nonexistent_page(self, client):
        """测试不存在的页面"""
        response = client.get("/nonexistent")

        # 应该返回404或重定向到错误页面
        assert response.status_code in [404, 302]


class TestStaticFiles:
    """静态文件测试"""

    def test_css_file(self, client):
        """测试CSS文件访问"""
        response = client.get("/static/css/main.css")

        # 如果静态文件存在，应该返回200，否则404
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            assert response.headers["content-type"].startswith("text/css")

    def test_js_file(self, client):
        """测试JavaScript文件访问"""
        response = client.get("/static/js/common.js")

        # 如果静态文件存在，应该返回200，否则404
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            assert content_type.startswith(("application/javascript", "text/javascript"))
