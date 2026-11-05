from unittest.mock import MagicMock
from services.database_service import DatabaseService


def test_database_service_create_and_load_conversations():
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "conv-1", "user_id": "user-1", "title": "Test Chat", "created_at": "2026-11-05T10:00:00Z"}
    ]
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {
            "id": "conv-1",
            "title": "Test Chat",
            "created_at": "2026-11-05T10:00:00Z",
            "messages": [
                {
                    "id": "msg-1",
                    "role": "user",
                    "content": "Bonjour",
                    "created_at": "2026-11-05T10:01:00Z",
                    "analyses": [
                        {
                            "predicted_class": "fromage sain",
                            "confidence": 98.0,
                            "probabilities": {"fromage sain": 98.0},
                            "model_version": "1.0",
                        }
                    ],
                }
            ],
        }
    ]

    service = DatabaseService(supabase_client=mock_supabase)
    created = service.create_conversation("user-1", "Test Chat")
    assert created["id"] == "conv-1"

    convs = service.load_conversations("user-1")
    assert len(convs) == 1
    assert convs[0]["title"] == "Test Chat"
    assert len(convs[0]["messages"]) == 1
    assert convs[0]["messages"][0]["analysis"]["predicted_class"] == "fromage sain"


def test_database_service_delete_conversation():
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []

    service = DatabaseService(supabase_client=mock_supabase)
    service.delete_conversation("user-1", "conv-123")
    mock_supabase.table.assert_called_with("conversations")

