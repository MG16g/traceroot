from app.tools.metric_tool import query_metrics


def test_query_metrics_returns_all_metrics():
    results = query_metrics("INC-001")

    assert len(results) == 7


def test_query_metrics_filters_by_service():
    results = query_metrics(
        "INC-001",
        service="payment-service",
    )

    assert len(results) == 6

    assert all(
        record["service"] == "payment-service"
        for record in results
    )


def test_query_metrics_filters_by_metric():
    results = query_metrics(
        "INC-001",
        metric="db_connection_utilization",
    )

    assert len(results) == 5

    assert all(
        record["metric"] == "db_connection_utilization"
        for record in results
    )

def test_query_metrics_combines_filters():
    results = query_metrics(
        "INC-001",
        service="payment-service",
        metric="db_connection_utilization",
    )

    assert len(results) == 5

    assert all(
        record["service"] == "payment-service"
        and record["metric"] == "db_connection_utilization"
        for record in results
    )

def test_query_metrics_filters_by_time_window():
    results = query_metrics(
        "INC-001",
        metric="db_connection_utilization",
        start_time="2026-09-18T14:05:00Z",
        end_time="2026-09-18T14:12:00Z",
    )

    assert len(results) == 4

    assert [record["value"] for record in results] == [
        51.0,
        67.0,
        81.0,
        98.0,
    ]