from services.auth_service import AuthService


def test_local_user_can_sign_up_and_sign_in(tmp_path):
    auth = AuthService(tmp_path / "users.db")
    created = auth.sign_up("henri", "motdepasse123")
    signed_in = auth.sign_in("HENRI", "motdepasse123")
    assert signed_in.id == created.id
    assert signed_in.username == "henri"


class FakeTable:
    def upsert(self, data, on_conflict):
        self.data, self.conflict = data, on_conflict
        return self

    def execute(self):
        return self


class FakeSupabase:
    def __init__(self):
        self.users = FakeTable()

    def table(self, name):
        assert name == "users"
        return self.users


def test_new_user_is_synced_to_supabase(tmp_path):
    remote = FakeSupabase()
    user = AuthService(tmp_path / "users.db", remote_client=remote).sign_up("alice", "motdepasse123")
    assert remote.users.data["id"] == user.id
    assert remote.users.data["username"] == "alice"
