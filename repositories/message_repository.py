from repositories.base_repository import BaseRepository
class MessageRepository(BaseRepository):
    def __init__(self, client): super().__init__(client, "messages")
