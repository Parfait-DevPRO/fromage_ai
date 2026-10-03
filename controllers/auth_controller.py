from services.auth_service import AuthService


class AuthController:
    def __init__(self):
        # Account creation must not silently succeed only in local SQLite.
        self.service = AuthService(require_remote=True)

    def sign_in(self, username: str, password: str):
        return self.service.sign_in(username, password)

    def sign_up(self, username: str, password: str):
        return self.service.sign_up(username, password)
