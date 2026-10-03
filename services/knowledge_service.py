class KnowledgeService:
    """Future extension point for document retrieval/RAG."""
    def search(self, query: str) -> list[str]:
        return []
