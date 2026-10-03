from services.auth_service import AuthService


class AuthController:
    def __init__(self):
        self.service = AuthService()

    def sign_in(self, username: str, password: str):
        return self.service.sign_in(username, password)

    def sign_up(self, username: str, password: str):
        return self.service.sign_up(username, password)
