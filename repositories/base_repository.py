"""Thin repository base. Services use it when Supabase persistence is enabled."""

class BaseRepository:
    def __init__(self, client, table: str):
        self.client, self.table = client, table

    def create(self, data: dict):
        return self.client.table(self.table).insert(data).execute().data

    def get(self, record_id: str):
        response = self.client.table(self.table).select("*").eq("id", record_id).execute()
        return response.data[0] if response.data else None
