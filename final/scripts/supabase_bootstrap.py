import os
import json
from uuid import uuid4

from supabase import create_client


def getenv_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def table_exists(client, table_name: str) -> tuple[bool, str]:
    try:
        client.table(table_name).select("*", count="exact").limit(1).execute()
        return True, ""
    except Exception as exc:
        return False, str(exc)


def seed_users(client) -> dict:
    user_id = str(uuid4())
    email = f"seed-{user_id[:8]}@example.com"
    api_token = str(uuid4())

    payload = {
        "id": user_id,
        "email": email,
        "api_token": api_token,
    }

    result = client.table("users").insert(payload).execute()
    row = result.data[0] if result.data else payload
    return row


def seed_monitor_settings(client, user_id: str) -> dict:
    payload = {
        "user_id": user_id,
        "interval_seconds": 60,
        "threshold": 0.85,
    }
    result = client.table("monitor_settings").upsert(payload, on_conflict="user_id").execute()
    row = result.data[0] if result.data else payload
    return row


def main() -> None:
    supabase_url = getenv_required("SUPABASE_URL")
    service_key = getenv_required("SUPABASE_SERVICE_ROLE_KEY")

    client = create_client(supabase_url, service_key)

    report = {
        "project": supabase_url,
        "tables": {},
        "seed": {},
        "sql_required": False,
    }

    for table_name in ("users", "monitor_settings"):
        exists, message = table_exists(client, table_name)
        report["tables"][table_name] = {
            "exists": exists,
            "error": message if not exists else "",
        }

    if report["tables"]["users"]["exists"] and report["tables"]["monitor_settings"]["exists"]:
        user_row = seed_users(client)
        settings_row = seed_monitor_settings(client, user_row["id"])
        report["seed"]["users"] = user_row
        report["seed"]["monitor_settings"] = settings_row
    else:
        report["sql_required"] = True
        report["next_step"] = "Run scripts/supabase_schema.sql in Supabase SQL Editor, then re-run this script."

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
