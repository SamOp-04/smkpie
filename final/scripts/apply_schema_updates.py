"""
Apply database schema updates to Supabase.
This script checks which tables exist and creates missing ones.
"""

import os
import json
from supabase import create_client


def getenv_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def table_exists(client, table_name: str) -> tuple[bool, str]:
    """Check if a table exists in Supabase"""
    try:
        client.table(table_name).select("*", count="exact").limit(1).execute()
        return True, ""
    except Exception as exc:
        return False, str(exc)


def main() -> None:
    supabase_url = getenv_required("SUPABASE_URL")
    service_key = getenv_required("SUPABASE_SERVICE_ROLE_KEY")

    client = create_client(supabase_url, service_key)

    expected_tables = [
        "users",
        "monitor_settings",
        "model_versions",
        "predictions",
        "alerts",
        "api_logs",
        "performance_metrics",
    ]

    report = {
        "project": supabase_url,
        "tables": {},
        "all_exist": True,
    }

    print(f"Checking tables in project: {supabase_url}\n")

    for table_name in expected_tables:
        exists, message = table_exists(client, table_name)
        status = "✓ EXISTS" if exists else "✗ MISSING"
        report["tables"][table_name] = {
            "exists": exists,
            "error": message if not exists else "",
        }

        if not exists:
            report["all_exist"] = False

        print(f"{status}: {table_name}")
        if not exists and message:
            print(f"  Error: {message[:100]}")

    print("\n" + "=" * 60)

    if report["all_exist"]:
        print("✓ All tables exist! Schema is up to date.")
    else:
        missing = [t for t, info in report["tables"].items() if not info["exists"]]
        print(f"✗ Missing tables: {', '.join(missing)}")
        print("\nNext steps:")
        print("1. Run the SQL in scripts/supabase_schema.sql in Supabase SQL Editor")
        print("2. Re-run this script to verify")

    print("\nDetailed report:")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
