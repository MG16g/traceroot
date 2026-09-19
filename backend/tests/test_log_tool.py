from app.tools.log_tool import search_logs


def test_search_logs_returns_all_logs():
    results = search_logs("INC-001")

    assert len(results) > 0


def test_search_logs_filters_by_service():
    results = search_logs(
        "INC-001",
        service="payment-service",
    )

    assert len(results) > 0

    assert all(
        log["service"] == "payment-service"
        for log in results
    )

def test_search_logs_filters_by_level():
    results = search_logs(
        "INC-001",
        level="ERROR",
    )

    assert len(results) > 0

    assert all(
        log["level"] == "ERROR"
        for log in results
    )

def test_search_logs_filters_by_query():
    results = search_logs(
        "INC-001",
        query="CONNECTION",
    )

    assert len(results) > 0

    assert all(
        "connection" in log["message"].lower()
        for log in results
    )


def test_search_logs_combines_filters():
    results = search_logs(
        "INC-001",
        service="payment-service",
        level="ERROR",
        query="connection",
    )

    assert len(results) > 0

    assert all(
        log["service"] == "payment-service"
        and log["level"] == "ERROR"
        and "connection" in log["message"].lower()
        for log in results
    )

def test_search_logs_returns_empty_list_when_no_match():
    results = search_logs(
        "INC-001",
        query="THIS_DOES_NOT_EXIST",
    )

    assert results == []