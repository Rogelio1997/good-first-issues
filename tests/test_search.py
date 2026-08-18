import importlib
import pytest
from click.testing import CliRunner


search_module = importlib.import_module("good_first_issues.commands.search")


class FakeSpinner:
    def __init__(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def succeed(self, *args):
        pass


@pytest.fixture
def runner(monkeypatch):
    monkeypatch.setattr(search_module, "Halo", FakeSpinner)
    monkeypatch.setattr(search_module.utils, "check_credential", lambda: "token")
    return CliRunner()


def test_all_requests_maximum_page_size_for_org_search(monkeypatch, runner):
    requested_variables = {}

    def fake_caller(token, query, variables):
        requested_variables.update(variables)
        return {}

    monkeypatch.setattr(search_module.services, "caller", fake_caller)
    monkeypatch.setattr(
        search_module.services, "org_user_pipeline", lambda response, mode: ([], 100)
    )

    result = runner.invoke(search_module.search, ["example", "--all"])

    assert result.exit_code == 0
    assert requested_variables["limit"] == 100


def test_all_does_not_truncate_hacktoberfest_results(monkeypatch, runner):
    issues = [
        (f"Issue {number}", f"https://example.test/{number}")
        for number in range(12)
    ]
    displayed_rows = []

    monkeypatch.setattr(search_module.services, "caller", lambda *args: {})
    monkeypatch.setattr(
        search_module.services,
        "extract_search_results",
        lambda response: (issues, 100),
    )
    monkeypatch.setattr(
        search_module,
        "tabulate",
        lambda rows, headers, **kwargs: displayed_rows.extend(rows) or "",
    )

    result = runner.invoke(search_module.search, ["--hacktoberfest", "--all"])

    assert result.exit_code == 0
    assert displayed_rows == issues
