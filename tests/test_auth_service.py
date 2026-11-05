from services.auth_service import AuthService
from unittest.mock import patch, MagicMock


def test_auth_service_validate():
    username, password = AuthService._validate("henri", "motdepasse123")
    assert username == "henri"
    assert password == "motdepasse123"


def test_auth_service_to_email():
    assert AuthService._to_email("henri") == "henri@fromazy.app"
    assert AuthService._to_email("HENRI") == "henri@fromazy.app"
    assert AuthService._to_email("test@example.com") == "test@example.com"


def test_auth_service_sign_in_mock():
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"id": "test-uuid-123", "username": "alice", "display_name": "Alice"}
    ]
    fake_secrets = {
        "SUPABASE_URL": "https://ci-test.supabase.co",
        "SUPABASE_KEY": "sb_secret_ci_test_key",
    }

    with (
        patch("services.auth_service.secret", side_effect=fake_secrets.get),
        patch("requests.post") as mock_post,
    ):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "user": {"id": "test-uuid-123"}
        }

        auth = AuthService(remote_client=mock_client)
        user = auth.sign_in("alice", "password123")
        assert user.id == "test-uuid-123"
        assert user.username == "alice"
        assert user.display_name == "Alice"
        mock_post.assert_called_once_with(
            "https://ci-test.supabase.co/auth/v1/token?grant_type=password",
            json={"email": "alice@fromazy.app", "password": "password123"},
            headers=auth.headers,
            timeout=12,
        )
