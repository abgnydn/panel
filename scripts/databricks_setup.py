"""
Panel — Databricks workspace bootstrap.

Drives the whole Step-1 setup from the CLI:
  1. Create catalog `panel` + schema `panel.main`
  2. Create volume `panel.main.seed`
  3. Upload the 4 JSON seed files to that volume
  4. Create Delta tables from each JSON

Run:
    cd ~/panel
    .venv/bin/python scripts/databricks_setup.py

Requires:
  - `databricks auth login --host <workspace-url>` already done
  - The serverless SQL warehouse available in the workspace

Idempotent — re-run as needed.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "app" / "data"

CATALOG = "panel"
SCHEMA = "main"
VOLUME = "seed"
FQ_VOLUME = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"


def main() -> None:
    w = WorkspaceClient()
    print(f"Connected as {w.current_user.me().user_name}\n")

    warehouse_id = pick_warehouse(w)
    print(f"Using warehouse: {warehouse_id}\n")

    print("─── Catalog + schema + volume ───")
    run_sql(w, warehouse_id, "CREATE CATALOG IF NOT EXISTS panel "
            "COMMENT 'Panel — multi-agent rights advisor'")
    run_sql(w, warehouse_id, f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA} "
            "COMMENT 'Reference data + case archive'")
    run_sql(w, warehouse_id,
            f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{VOLUME} "
            "COMMENT 'Raw JSON seed files'")

    print("\n─── Uploading seed files ───")
    for name in ["labor_codes", "ilo_standards", "case_archive", "embassy_directory"]:
        upload_seed(w, name)

    print("\n─── Creating Delta tables ───")
    create_labor_codes_table(w, warehouse_id)
    create_ilo_standards_table(w, warehouse_id)
    create_case_archive_table(w, warehouse_id)
    create_embassy_directory_table(w, warehouse_id)

    print("\n─── Verifying ───")
    res = run_sql(w, warehouse_id,
                  f"SELECT table_name, table_type FROM {CATALOG}.information_schema.tables "
                  f"WHERE table_schema = '{SCHEMA}' ORDER BY table_name",
                  fetch=True)
    print("Tables in panel.main:")
    for row in res or []:
        print(f"  • {row[0]:30s} {row[1]}")

    print("\nDone. ✓")


# ---------------------------------------------------------------------------
def pick_warehouse(w: WorkspaceClient) -> str:
    """Find a usable SQL warehouse — prefer serverless."""
    for wh in w.warehouses.list():
        if wh.enable_serverless_compute and wh.id:
            return wh.id
    # Fallback: any warehouse
    for wh in w.warehouses.list():
        if wh.id:
            return wh.id
    raise RuntimeError("No SQL warehouse found")


def run_sql(w: WorkspaceClient, warehouse_id: str, sql: str, *,
            fetch: bool = False) -> list[list[str]] | None:
    """Execute a SQL statement via the Statement Execution API.

    Returns rows if fetch=True, else None. Raises on FAILED state.
    """
    print(f"  → {sql[:100]}{'…' if len(sql) > 100 else ''}")
    resp = w.statement_execution.execute_statement(
        warehouse_id=warehouse_id,
        statement=sql,
        wait_timeout="30s",
    )
    sid = resp.statement_id
    state = resp.status.state if resp.status else None

    # Poll if still pending
    while state in (StatementState.PENDING, StatementState.RUNNING):
        time.sleep(0.8)
        info = w.statement_execution.get_statement(sid)
        state = info.status.state if info.status else None
        resp = info

    if state == StatementState.FAILED:
        err = resp.status.error if (resp.status and resp.status.error) else "unknown"
        raise RuntimeError(f"SQL failed: {err}")

    if fetch and resp.result and resp.result.data_array:
        return resp.result.data_array
    return None


def upload_seed(w: WorkspaceClient, name: str) -> None:
    src = DATA_DIR / f"{name}.json"
    if not src.exists():
        print(f"  ✗ {name}.json not found at {src}")
        return
    dest = f"{FQ_VOLUME}/{name}.json"
    with src.open("rb") as fh:
        w.files.upload(file_path=dest, contents=fh, overwrite=True)
    print(f"  ✓ {dest}")


# ---------------------------------------------------------------------------
# Delta table builders — each JSON has a different shape, so each gets a
# bespoke SQL that uses Databricks' native JSON reader and explodes / parses
# the structure into a typed table.
# ---------------------------------------------------------------------------
def create_labor_codes_table(w: WorkspaceClient, warehouse_id: str) -> None:
    sql = f"""
    CREATE OR REPLACE TABLE {CATALOG}.{SCHEMA}.labor_codes AS
    WITH raw AS (
      SELECT * FROM read_files(
        '{FQ_VOLUME}/labor_codes.json',
        format => 'json',
        multiLine => true
      )
    )
    SELECT
      country_code,
      country_block.country_name AS country_name,
      country_block.instrument   AS instrument,
      statute_topic,
      statute.citation     AS citation,
      statute.rule         AS rule,
      statute.since        AS since,
      statute.enforcement  AS enforcement,
      statute.note         AS note
    FROM raw
    LATERAL VIEW explode(map_entries(named_struct())) AS dummy_kv -- placeholder
    """
    # Simpler approach: load the JSON as a Python dict, generate INSERT rows
    src = DATA_DIR / "labor_codes.json"
    data = json.loads(src.read_text())
    rows: list[tuple] = []
    for country_code, block in data.items():
        name = block.get("country_name", "")
        instrument = block.get("instrument", "")
        for topic, statute in (block.get("statutes") or {}).items():
            rows.append((
                country_code,
                name,
                instrument,
                topic,
                statute.get("citation", ""),
                statute.get("rule", ""),
                str(statute.get("since", "")),
                statute.get("enforcement", "") or statute.get("note", ""),
            ))

    run_sql(w, warehouse_id, f"DROP TABLE IF EXISTS {CATALOG}.{SCHEMA}.labor_codes")
    run_sql(w, warehouse_id, f"""
    CREATE TABLE {CATALOG}.{SCHEMA}.labor_codes (
      country_code  STRING,
      country_name  STRING,
      instrument    STRING,
      statute_topic STRING,
      citation      STRING,
      rule          STRING,
      since         STRING,
      note          STRING
    ) USING DELTA
    COMMENT 'Destination-country labor codes — passport, hours, deductions, etc.'
    """)
    insert_rows(w, warehouse_id, "labor_codes", rows)
    print(f"  ✓ labor_codes ({len(rows)} rows)")


def create_ilo_standards_table(w: WorkspaceClient, warehouse_id: str) -> None:
    src = DATA_DIR / "ilo_standards.json"
    data = json.loads(src.read_text())
    rows: list[tuple] = []
    for convention_id, block in data.items():
        rows.append((
            convention_id,
            block.get("name", ""),
            int(block.get("year", 0)) if block.get("year") else None,
            "\n".join(block.get("key_principles") or []),
        ))
    run_sql(w, warehouse_id, f"DROP TABLE IF EXISTS {CATALOG}.{SCHEMA}.ilo_standards")
    run_sql(w, warehouse_id, f"""
    CREATE TABLE {CATALOG}.{SCHEMA}.ilo_standards (
      id             STRING,
      name           STRING,
      year           INT,
      key_principles STRING
    ) USING DELTA
    COMMENT 'ILO conventions + ASEAN standard contract reference'
    """)
    insert_rows(w, warehouse_id, "ilo_standards", rows)
    print(f"  ✓ ilo_standards ({len(rows)} rows)")


def create_case_archive_table(w: WorkspaceClient, warehouse_id: str) -> None:
    src = DATA_DIR / "case_archive.json"
    data = json.loads(src.read_text())
    rows = [
        (
            c["id"],
            c["source"],
            c.get("country_of_origin", ""),
            c.get("destination_country", ""),
            c.get("clause_category", ""),
            c.get("outcome", ""),
            c.get("anonymized_facts", ""),
            int(c.get("year", 0)) if c.get("year") else None,
        )
        for c in data
    ]
    run_sql(w, warehouse_id, f"DROP TABLE IF EXISTS {CATALOG}.{SCHEMA}.case_archive")
    run_sql(w, warehouse_id, f"""
    CREATE TABLE {CATALOG}.{SCHEMA}.case_archive (
      id                  STRING,
      source              STRING,
      country_of_origin   STRING,
      destination_country STRING,
      clause_category     STRING,
      outcome             STRING,
      anonymized_facts    STRING,
      year                INT
    ) USING DELTA
    COMMENT 'Anonymized historical cases — Peer Advocate source'
    """)
    insert_rows(w, warehouse_id, "case_archive", rows)
    print(f"  ✓ case_archive ({len(rows)} rows)")


def create_embassy_directory_table(w: WorkspaceClient, warehouse_id: str) -> None:
    src = DATA_DIR / "embassy_directory.json"
    data = json.loads(src.read_text())
    rows = [
        (
            c["country_of_origin"],
            c["located_in_country"],
            c["name"],
            c.get("phone", ""),
            c.get("whatsapp", ""),
            c.get("email", ""),
            bool(c.get("is_24h_hotline", False)),
            ",".join(c.get("languages") or []),
        )
        for c in data
    ]
    run_sql(w, warehouse_id, f"DROP TABLE IF EXISTS {CATALOG}.{SCHEMA}.embassy_directory")
    run_sql(w, warehouse_id, f"""
    CREATE TABLE {CATALOG}.{SCHEMA}.embassy_directory (
      country_of_origin   STRING,
      located_in_country  STRING,
      name                STRING,
      phone               STRING,
      whatsapp            STRING,
      email               STRING,
      is_24h_hotline      BOOLEAN,
      languages           STRING
    ) USING DELTA
    COMMENT 'Embassy + NGO contact directory for Triage agent'
    """)
    insert_rows(w, warehouse_id, "embassy_directory", rows)
    print(f"  ✓ embassy_directory ({len(rows)} rows)")


def insert_rows(w: WorkspaceClient, warehouse_id: str, table: str,
                rows: list[tuple]) -> None:
    """INSERT row-by-row via parameterised SQL — small tables, simpler than
    spinning up a Spark write. Uses VALUES clause batched in chunks of 50."""
    BATCH = 50
    full = f"{CATALOG}.{SCHEMA}.{table}"
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i + BATCH]
        values_sql = ",\n".join("(" + ",".join(sql_literal(v) for v in row) + ")"
                                 for row in chunk)
        run_sql(w, warehouse_id, f"INSERT INTO {full} VALUES\n{values_sql}")


def sql_literal(v) -> str:
    """Render a Python value as a SQL literal. Strings get quoted + escaped."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("'", "''")
    return f"'{s}'"


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
