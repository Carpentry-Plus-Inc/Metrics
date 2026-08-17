from typing import Any, Dict, List, Optional

from supabase import create_client


class SupabaseClient:
    """Minimal self-contained Supabase client for the project dashboard."""

    def __init__(self, url: str, key: str):
        if not url or not key:
            raise ValueError("Supabase URL and key are required")
        self._client = create_client(url, key)

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        query = self._client.table(table).select(columns)
        if filters:
            for col, val in filters.items():
                query = query.eq(col, val)
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.execute().data or []


def get_supabase_client(url: str, key: str) -> SupabaseClient:
    return SupabaseClient(url, key)
