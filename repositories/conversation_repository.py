from repositories.base_repository import BaseRepository
class ConversationRepository(BaseRepository):
    def __init__(self, client): super().__init__(client, "conversations")
