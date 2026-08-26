import pytest
import requests

from good_first_issues.graphql import services


def test_caller_handles_connection_error(monkeypatch):
    def raise_connection_error(*args, **kwargs):
        raise requests.exceptions.ConnectionError("network unavailable")

    monkeypatch.setattr(requests.Session, "post", raise_connection_error)

    with pytest.raises(SystemExit):
        services.caller("token", "query", {})
