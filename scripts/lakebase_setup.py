"""
Provision Lakebase schema for Panel.

Connects to the `panel-db` Lakebase instance using a Databricks OAuth token
as the Postgres password (Lakebase's auth model), runs the lakebase/
001_schema.sql against it, verifies tables exist.
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg
from databricks.sdk import WorkspaceClient

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_SQL = ROOT / "lakebase" / "001_schema.sql"
INSTANCE = "panel-db"
DB_NAME = "databricks_postgres"  # Lakebase default database


def main() -> None:
    w = WorkspaceClient()
    print(f"Connected as {w.current_user.me().user_name}")

    inst = w.database.get_database_instance(name=INSTANCE)
    print(f"Lakebase: {inst.name} ({inst.state}) · {inst.read_write_dns}")

    # Generate a database credential (OAuth token Lakebase accepts as password)
    cred = w.database.generate_database_credential(
        instance_names=[INSTANCE],
        request_id="panel-bootstrap",
    )
    token = cred.token
    print(f"  • OAuth credential generated ({len(token)} chars)")

    # Connect
    me = w.current_user.me().user_name
    dsn = (
        f"host={inst.read_write_dns} "
        f"dbname={DB_NAME} "
        f"user={me} "
        f"password={token} "
        f"sslmode=require"
    )

    with psycopg.connect(dsn, autocommit=True) as conn:
        print(f"  • Connected to {DB_NAME} as {me}")
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            print(f"  • {cur.fetchone()[0][:60]}…")

            # pgvector — try to enable; degrade gracefully
            try:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                print("  • pgvector enabled")
                has_vector = True
            except Exception as e:
                print(f"  • pgvector unavailable: {e}")
                has_vector = False

            sql = SCHEMA_SQL.read_text(encoding="utf-8")
            if not has_vector:
                sql = sql.replace("CREATE EXTENSION IF NOT EXISTS vector;", "")
                sql = sql.replace("embedding           VECTOR(1024),", "")
                sql = sql.replace(
                    "CREATE INDEX IF NOT EXISTS idx_case_archive_embedding\n"
                    "    ON case_archive USING ivfflat (embedding vector_cosine_ops);",
                    "",
                )

            # Strip BEGIN/COMMIT (autocommit handles transactions per statement)
            # and split on bare semicolons at end of line (avoids splitting in
            # INTERVAL '24 hours' kind of strings).
            sql = sql.replace("BEGIN;", "").replace("COMMIT;", "")
            statements: list[str] = []
            current: list[str] = []
            for line in sql.split("\n"):
                stripped = line.strip()
                if stripped.startswith("--") or not stripped:
                    continue
                current.append(line)
                if stripped.endswith(";"):
                    stmt = "\n".join(current).rstrip().rstrip(";").strip()
                    if stmt:
                        statements.append(stmt)
                    current = []
            if current:
                tail = "\n".join(current).strip()
                if tail:
                    statements.append(tail)

            print(f"  • Parsed {len(statements)} statements")
            for i, stmt in enumerate(statements, 1):
                preview = stmt.split("\n")[0][:60]
                try:
                    cur.execute(stmt)
                    print(f"    {i:2d}. ✓ {preview}")
                except Exception as e:
                    print(f"    {i:2d}. ✗ {preview} — {e}")

            cur.execute("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)
            tables = [r[0] for r in cur.fetchall()]
            print("\nTables in panel-db:")
            for t in tables:
                print(f"  • {t}")

    print("\nDone. ✓")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
