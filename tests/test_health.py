"""
健康检查端点测试
"""
def test_health_check(client):
    """测试健康检查端点"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "uptime" in data


def test_health_check_format(client):
    """测试健康检查响应格式"""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    data = response.json()

    # 验证响应结构
    required_fields = ["status", "timestamp", "version", "uptime"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # 验证数据类型
    assert isinstance(data["status"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["uptime"], (int, float))
