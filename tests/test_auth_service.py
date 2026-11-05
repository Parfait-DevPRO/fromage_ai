from services.auth_service import AuthService, LocalUser
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

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "user": {"id": "test-uuid-123"}
        }

        auth = AuthService(remote_client=mock_client)
        user = auth.sign_in("alice", "password123")
        assert user.id == "test-uuid-123"
        assert user.username == "alice"
        assert user.display_name == "Alice"
