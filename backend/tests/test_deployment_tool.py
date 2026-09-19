from app.tools.deployment_tool import get_deployments



def test_get_deployments_returns_all():
    results = get_deployments("INC-001")

    assert len(results) == 2


def test_get_deployments_filters_by_service():
    results = get_deployments(
        "INC-001",
        service="payment-service",
    )

    assert len(results) == 1
    assert results[0]["deployment_id"] == "DEP-1001"
    assert results[0]["service"] == "payment-service"


def test_get_deployments_filters_by_status():
    results = get_deployments(
        "INC-001",
        status="success",
    )

    assert len(results) == 2

    assert all(
        record["status"] == "success"
        for record in results
    )

def test_get_deployments_filters_by_time_window():
    results = get_deployments(
        "INC-001",
        start_time="2026-09-18T14:05:00Z",
        end_time="2026-09-18T14:10:00Z",
    )

    assert len(results) == 1
    assert results[0]["deployment_id"] == "DEP-1001"


def test_get_deployments_combines_filters():
    results = get_deployments(
        "INC-001",
        service="payment-service",
        status="success",
        start_time="2026-09-18T14:00:00Z",
        end_time="2026-09-18T14:10:00Z",
    )

    assert len(results) == 1

    deployment = results[0]

    assert deployment["deployment_id"] == "DEP-1001"
    assert deployment["service"] == "payment-service"
    assert deployment["status"] == "success"