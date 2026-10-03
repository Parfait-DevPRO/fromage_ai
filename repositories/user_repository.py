from repositories.base_repository import BaseRepository
class UserRepository(BaseRepository):
    def __init__(self, client): super().__init__(client, "users")
