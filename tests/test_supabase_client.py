import sys
from types import ModuleType

import pytest

import config.supabase_client as supabase_client


@pytest.mark.parametrize(
    ("key", "expected_authorization"),
    [
        ("header.payload.signature", "Bearer header.payload.signature"),
        ("sb_secret_test", None),
    ],
)
def test_postgrest_client_uses_the_correct_auth_header(monkeypatch, key, expected_authorization):
    captured = {}

    def reject_supabase_client(*args, **kwargs):
        raise RuntimeError("Force the PostgREST fallback")

    class FakePostgrestClient:
        def __init__(self, url, headers):
            captured["url"] = url
            captured["headers"] = headers

    supabase_module = ModuleType("supabase")
    supabase_module.create_client = reject_supabase_client
    postgrest_module = ModuleType("postgrest")
    postgrest_module.SyncPostgrestClient = FakePostgrestClient
    monkeypatch.setitem(sys.modules, "supabase", supabase_module)
    monkeypatch.setitem(sys.modules, "postgrest", postgrest_module)

    client = supabase_client.get_supabase_client("https://example.supabase.co", key)

    assert client is not None
    assert captured["url"] == "https://example.supabase.co/rest/v1"
    if expected_authorization is None:
        assert "Authorization" not in captured["headers"]
    else:
        assert captured["headers"]["Authorization"] == expected_authorization


def test_connection_diagnostic_uses_bearer_for_legacy_jwt(monkeypatch):
    requests_module = supabase_client.requests
    captured = []

    class Response:
        status_code = 200
        text = ""

    def fake_get(url, headers, timeout):
        captured.append(headers)
        return Response()

    def fake_post(url, json, headers, timeout):
        captured.append(headers)
        response = Response()
        response.status_code = 403
        return response

    monkeypatch.setattr(requests_module, "get", fake_get)
    monkeypatch.setattr(requests_module, "post", fake_post)
    monkeypatch.setattr(requests_module, "delete", lambda *args, **kwargs: Response())

    result = supabase_client.test_supabase_connection(
        "https://example.supabase.co",
        "header.payload.signature",
    )

    assert result["status"] == "connected_read_only"
    assert captured[1]["Authorization"] == "Bearer header.payload.signature"
