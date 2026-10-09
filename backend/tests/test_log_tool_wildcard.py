from app.tools.log_tool import search_logs


def test_wildcard_query_matches_unfiltered_logs():
    expected = search_logs(
        incident_id="INC-001",
        service="payment-service",
    )

    actual = search_logs(
        incident_id="INC-001",
        service="payment-service",
        query="*",
    )

    assert len(expected) > 0
    assert actual == expected


def test_empty_query_matches_unfiltered_logs():
    expected = search_logs(
        incident_id="INC-001",
        service="payment-service",
    )

    actual = search_logs(
        incident_id="INC-001",
        service="payment-service",
        query="",
    )

    assert actual == expected


def test_whitespace_query_matches_unfiltered_logs():
    expected = search_logs(
        incident_id="INC-001",
        service="payment-service",
    )

    actual = search_logs(
        incident_id="INC-001",
        service="payment-service",
        query="   ",
    )

    assert actual == expected


def test_regular_query_preserves_message_filtering():
    logs = search_logs(
        incident_id="INC-001",
        service="payment-service",
        query="connection",
    )

    assert all(
        "connection" in log["message"].lower()
        for log in logs
    )