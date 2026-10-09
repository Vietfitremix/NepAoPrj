"""Generate immutable Flyway seed SQL or import unchanged asset bytes into PostgreSQL.

Run with ../ai-service/.venv/Scripts/python.exe from the repository root:
  backend/import_data.py --generate-seed
  backend/import_data.py --assets
No source assets are modified; an identical second asset import is a no-op.
"""
import argparse
import hashlib
import json
import mimetypes
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def documents():
    result = {}
    for path in sorted((ROOT / "ai-service/data").glob("*.json")):
        result["ai." + path.stem] = (path, json.loads(path.read_text(encoding="utf-8")))
    for character in ("male", "female"):
        path = ROOT / f"frontend/public/figure/{character}-layers/catalog.json"
        result["wardrobe." + character] = (path, json.loads(path.read_text(encoding="utf-8")))
    path = ROOT / "frontend/public/figure/patterns/catalog.json"
    result["wardrobe.patterns"] = (path, json.loads(path.read_text(encoding="utf-8")))
    path = ROOT / "frontend/src/utils/wardrobeStyles.ts"
    colors = [{"name": name, "value": value} for name, value in
              re.findall(r"\{name:'([^']+)',value:'(#[a-fA-F0-9]{6})'\}", path.read_text(encoding="utf-8"))]
    if not colors:
        raise ValueError("Existing wardrobe colors not found")
    result["wardrobe.colors"] = (path, colors)
    return result


def sql_value(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def json_value(value):
    return "CAST(" + sql_value(json.dumps(value, ensure_ascii=False, separators=(",", ":"))) + " AS JSONB)"


def generate_seed():
    docs = documents()
    lines = ["-- Source snapshot of existing files. Do not change after this migration is applied."]

    def insert(table, columns, values, json_columns=()):
        serialized = [json_value(v) if i in json_columns else sql_value(v) for i, v in enumerate(values)]
        lines.append(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(serialized)});")

    for key, (path, payload) in docs.items():
        insert("data_documents", ["data_key", "source_path", "sha256", "payload"],
               [key, path.relative_to(ROOT).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest(), payload], [3])
    for character in ("male", "female"):
        catalog = docs["wardrobe." + character][1]
        for category in ("outfits", "pants", "shoes", "accessories"):
            for item in catalog[category]:
                insert("wardrobe_items", ["character", "category", "item_key", "display_name", "slot", "metadata"],
                       [character, category, item["id"], item["name"], item.get("slot"), item], [5])
    for dataset in ("occasions", "styles", "garments", "accessories", "palettes", "patterns", "culture-cards"):
        for item in docs["ai." + dataset][1]:
            insert("ai_catalog_entries", ["dataset_key", "entry_key", "metadata"], [dataset, item["id"], item], [2])
    for rule in docs["ai.rules"][1]:
        insert("ai_cultural_rules", ["rule_key", "criterion", "active", "verified", "metadata"],
               [rule["id"], rule.get("criterion"), rule.get("active", True), rule.get("verified", False), rule], [4])
    for index, question in enumerate(docs["ai.quiz"][1]):
        insert("quiz_questions", ["question_key", "sort_order", "metadata"], [question["id"], index, question], [2])
    for index, criterion in enumerate(docs["ai.scoring"][1]["criteria"]):
        insert("scoring_criteria", ["criterion_key", "sort_order", "metadata"], [criterion["id"], index, criterion], [2])
    for section, entries in docs["ai.checklist"][1].items():
        if section.startswith("_"):
            continue
        for key, value in (entries.items() if isinstance(entries, dict) else [(section, entries)]):
            insert("checklist_entries", ["section_key", "entry_key", "metadata"], [section, key, {"text": value}], [2])
    path = ROOT / "backend/src/main/resources/db/migration/V8__seed_existing_asset_and_ai_catalog.sql"
    if path.exists():
        raise FileExistsError("Seed already exists; use a new migration for future data changes")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {len(lines)-1} seed records from {len(docs)} documents.", flush=True)


def connect_database():
    import os
    import psycopg
    from dotenv import dotenv_values
    from urllib.parse import urlparse

    env_path = ROOT / ".env"
    settings = dotenv_values(env_path) if env_path.exists() else {}
    raw_url = os.environ.get("DATABASE_URL") or settings.get("DATABASE_URL", "jdbc:postgresql://localhost:5432/viet_fit")
    url = urlparse(raw_url.removeprefix("jdbc:"))
    user = os.environ.get("DATABASE_USERNAME") or settings.get("DATABASE_USERNAME", "viet_fit")
    password = os.environ.get("DATABASE_PASSWORD") or settings.get("DATABASE_PASSWORD", "")
    return psycopg.connect(host=url.hostname, port=url.port or 5432, dbname=url.path.lstrip("/"),
                          user=user, password=password, connect_timeout=10)


def import_assets():
    paths = sorted(p for folder in (ROOT / "frontend/public", ROOT / "assets") for p in folder.rglob("*") if p.is_file())
    with connect_database() as conn:
        existing = dict(conn.execute("SELECT relative_path,sha256 FROM asset_files").fetchall())
        changed = 0
        total_bytes = 0
        for index, path in enumerate(paths, 1):
            relative = path.relative_to(ROOT).as_posix()
            with path.open("rb") as source:
                digest = hashlib.file_digest(source, "sha256").hexdigest()
            total_bytes += path.stat().st_size
            if existing.get(relative) != digest:
                content = path.read_bytes()
                if hashlib.sha256(content).hexdigest() != digest:
                    raise RuntimeError("Source asset changed during import: " + relative)
                conn.execute("""INSERT INTO asset_files(relative_path,content_type,byte_size,sha256,file_data)
                    VALUES (%s,%s,%s,%s,%s) ON CONFLICT(relative_path) DO UPDATE SET
                    content_type=EXCLUDED.content_type,byte_size=EXCLUDED.byte_size,sha256=EXCLUDED.sha256,
                    file_data=EXCLUDED.file_data,updated_at=CURRENT_TIMESTAMP""",
                    (relative, mimetypes.guess_type(relative)[0] or "application/octet-stream", len(content), digest, content))
                changed += 1
            if index % 100 == 0 or index == len(paths):
                print(f"Assets checked {index}/{len(paths)}; imported {changed}; source bytes {total_bytes}", flush=True)
        # Verify all file bytes before publishing the transaction.
        count, size, valid = conn.execute("SELECT count(*),sum(byte_size),bool_and(octet_length(file_data)=byte_size) FROM asset_files").fetchone()
        if count < len(paths) or size < total_bytes or not valid:
            raise RuntimeError("Asset import verification failed")
    print(f"Committed {changed} asset files; {len(paths)} source files accounted for.", flush=True)


def audit_database(report_path):
    """Read-only audit: count every application table and verify stored asset bytes."""
    from datetime import datetime, timezone
    from psycopg import sql

    with connect_database() as conn:
        conn.execute("SET TRANSACTION READ ONLY")
        tables = conn.execute("""SELECT schemaname,tablename FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog','information_schema') AND schemaname NOT LIKE 'pg_toast%'
            ORDER BY schemaname,tablename""").fetchall()
        counts = {}
        for schema, table in tables:
            count = conn.execute(sql.SQL("SELECT count(*) FROM {}.{}").format(sql.Identifier(schema), sql.Identifier(table))).fetchone()[0]
            counts[schema + '.' + table] = count
            print(f"{schema}.{table}: {count}", flush=True)
        count, size, invalid = conn.execute("""SELECT count(*),sum(byte_size),
            count(*) FILTER (WHERE octet_length(file_data)<>byte_size OR encode(sha256(file_data),'hex')<>sha256)
            FROM asset_files""").fetchone()
        stored = dict(conn.execute("SELECT relative_path,sha256 FROM asset_files").fetchall())
        mismatches = []
        source_count = 0
        for folder in (ROOT / 'frontend/public', ROOT / 'assets'):
            for path in folder.rglob('*'):
                if not path.is_file(): continue
                source_count += 1
                with path.open('rb') as source:
                    digest = hashlib.file_digest(source, 'sha256').hexdigest()
                key = path.relative_to(ROOT).as_posix()
                if stored.get(key) != digest: mismatches.append(key)
        empty = [table for table, count in counts.items() if count == 0]
        report = {'checkedAt': datetime.now(timezone.utc).isoformat(), 'tables': counts, 'emptyTables': empty,
                  'assets': {'storedFiles': count, 'sourceFiles': source_count, 'storedBytes': int(size or 0),
                             'invalidStoredFiles': invalid, 'sourceMismatches': mismatches}}
    target = Path(report_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Audit: {len(counts)} tables; {len(empty)} empty; {invalid} invalid assets; {len(mismatches)} source mismatches.", flush=True)
    if empty or invalid or mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--generate-seed", action="store_true")
    modes.add_argument("--assets", action="store_true")
    modes.add_argument("--audit", action="store_true")
    parser.add_argument("--report", default=str(ROOT / ".tools/database-audit.json"))
    args = parser.parse_args()
    if args.generate_seed:
        generate_seed()
    elif args.assets:
        import_assets()
    else:
        audit_database(args.report)
