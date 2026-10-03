from repositories.base_repository import BaseRepository
class AnalysisRepository(BaseRepository):
    def __init__(self, client): super().__init__(client, "analyses")
