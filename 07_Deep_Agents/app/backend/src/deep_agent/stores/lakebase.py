"""Long-term memory store backed by a Databricks Lakebase (Postgres) instance.

Auth uses short-lived OAuth tokens issued by the Databricks SDK
(``WorkspaceClient.database.generate_database_credential``). Tokens are
refreshed on a TTL — connection pooling is intentionally avoided so each
operation grabs a fresh, valid credential.
"""

import uuid
from datetime import datetime, timedelta, timezone

import psycopg
from databricks.sdk import WorkspaceClient

from deep_agent.config import (
    LAKEBASE_DATABASE,
    LAKEBASE_INSTANCE_NAME,
    LAKEBASE_SCHEMA,
    LAKEBASE_TABLE,
)


FULL_TABLE = f"{LAKEBASE_SCHEMA}.{LAKEBASE_TABLE}"

# Single user mode — no auth
DEFAULT_USER_ID = "default-user"

# Refresh the OAuth token before the SDK-issued one expires (~1h)
_TOKEN_TTL = timedelta(minutes=50)


class LakebaseMemoryStore:
    """CRUD operations for long-term memories stored in a Lakebase Postgres table."""

    def __init__(self):
        self.client = WorkspaceClient()
        self._host: str | None = None
        self._username: str | None = None
        self._token: str | None = None
        self._token_expires_at = datetime.now(timezone.utc)

    def _resolve_endpoint(self) -> tuple[str, str]:
        if self._host is None:
            instance = self.client.database.get_database_instance(
                name=LAKEBASE_INSTANCE_NAME,
            )
            self._host = instance.read_write_dns
        if self._username is None:
            self._username = self.client.current_user.me().user_name
        return self._host, self._username

    def _get_token(self) -> str:
        now = datetime.now(timezone.utc)
        if self._token and now < self._token_expires_at:
            return self._token
        cred = self.client.database.generate_database_credential(
            request_id=str(uuid.uuid4()),
            instance_names=[LAKEBASE_INSTANCE_NAME],
        )
        self._token = cred.token
        self._token_expires_at = now + _TOKEN_TTL
        return self._token

    def _connect(self) -> psycopg.Connection:
        host, username = self._resolve_endpoint()
        return psycopg.connect(
            host=host,
            port=5432,
            dbname=LAKEBASE_DATABASE,
            user=username,
            password=self._get_token(),
            sslmode="require",
        )

    def ensure_table(self):
        """Create the memories table only if it doesn't already exist.

        Checks first via ``to_regclass`` so that callers without CREATE
        privilege on the schema (e.g. a service principal with only DML
        grants) can still initialise — the deployed app typically falls in
        this category since the table is provisioned once during dev.
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT to_regclass(%s)", (FULL_TABLE,))
            exists = cur.fetchone()[0] is not None
            if exists:
                return
            cur.execute(f"""
                CREATE TABLE {FULL_TABLE} (
                    id UUID PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general',
                    saved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            cur.execute(f"""
                CREATE INDEX agent_memories_user_saved_idx
                ON {FULL_TABLE} (user_id, saved_at DESC)
            """)

    def save(
        self,
        content: str,
        category: str = "general",
        user_id: str = DEFAULT_USER_ID,
    ) -> dict:
        memory_id = str(uuid.uuid4())
        saved_at = datetime.now(timezone.utc)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {FULL_TABLE} (id, user_id, content, category, saved_at) "
                f"VALUES (%s, %s, %s, %s, %s)",
                (memory_id, user_id, content, category, saved_at),
            )
        return {
            "id": memory_id,
            "content": content,
            "category": category,
            "saved_at": saved_at.isoformat(),
        }

    def recall(
        self,
        query: str = "",
        category: str = "",
        user_id: str = DEFAULT_USER_ID,
    ) -> list[dict]:
        clauses = ["user_id = %s"]
        params: list = [user_id]
        if category:
            clauses.append("category = %s")
            params.append(category)
        if query:
            clauses.append("content ILIKE %s")
            params.append(f"%{query}%")
        where = " AND ".join(clauses)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT id, content, category, saved_at "
                f"FROM {FULL_TABLE} WHERE {where} ORDER BY saved_at DESC",
                params,
            )
            rows = cur.fetchall()
            cols = [d.name for d in cur.description]
        return [dict(zip(cols, row)) for row in rows]

    def forget(
        self,
        content_substring: str,
        user_id: str = DEFAULT_USER_ID,
    ) -> dict | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {FULL_TABLE} "
                f"WHERE id = ("
                f"  SELECT id FROM {FULL_TABLE} "
                f"  WHERE user_id = %s AND content ILIKE %s "
                f"  ORDER BY saved_at DESC LIMIT 1"
                f") "
                f"RETURNING id, content",
                (user_id, f"%{content_substring}%"),
            )
            row = cur.fetchone()
        if not row:
            return None
        return {"id": str(row[0]), "content": row[1]}

    def list_all(self, user_id: str = DEFAULT_USER_ID) -> list[dict]:
        return self.recall(user_id=user_id)


# ============ Module-level singleton ============

_memory_db: LakebaseMemoryStore | None = None


def get_memory_db() -> LakebaseMemoryStore:
    """Return the process-wide memory store, creating it on first call."""
    global _memory_db
    if _memory_db is None:
        _memory_db = LakebaseMemoryStore()
    return _memory_db
