import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

import mysql.connector
from mysql.connector import Error

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("uwgym-mysql")

load_dotenv()

READ_ONLY_PATTERN = re.compile(r"^\s*(select|show|describe|explain)\b", re.IGNORECASE)


def get_conn():
    host = os.getenv("UWB_DB_HOST")
    port = int(os.getenv("UWB_DB_PORT", "3306"))
    user = os.getenv("UWB_DB_USER")
    password = os.getenv("UWB_DB_PASSWORD")
    database = os.getenv("UWB_DB_NAME")

    missing = [k for k, v in {
        "UWB_DB_HOST": host,
        "UWB_DB_USER": user,
        "UWB_DB_PASSWORD": password,
    }.items() if not v]

    if missing:
        raise RuntimeError(f"Missing required env var(s): {', '.join(missing)}")

    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        connection_timeout=10,
    )


def rows_as_dicts(cursor):
    cols = [c[0] for c in cursor.description] if cursor.description else []
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


@mcp.tool()
def sql_query(sql, params=None, limit=200):
    if not READ_ONLY_PATTERN.match(sql or ""):
        return {
            "ok": False,
            "error": "Only read-only statements are allowed (SELECT/SHOW/DESCRIBE/EXPLAIN).",
        }

    sql_stripped = sql.strip().rstrip(";")
    if re.search(r"\blimit\b", sql_stripped, flags=re.IGNORECASE) is None:
        sql_stripped = f"{sql_stripped} LIMIT {int(limit)}"

    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql_stripped, params or [])
        data = rows_as_dicts(cur)
        return {"ok": True, "rows": data, "row_count": len(data)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        try:
            if cur:
                cur.close()
        finally:
            if conn:
                conn.close()


@mcp.tool()
def list_locations():
    sql = """
    SELECT u.LocationId,
        u.LocationName,
        u.FacilityId,
        u.FacilityName,
        u.TotalCapacity,
        u.CountOfParticipants,
        u.PercetageCapacity,
        u.IsClosed,
        u.LastUpdatedDateAndTime
    FROM uwgyms u
    JOIN (
    SELECT LocationId, MAX(LastUpdatedDateAndTime) AS max_ts
    FROM uwgyms
    GROUP BY LocationId
    ) latest
    ON latest.LocationId = u.LocationId
    AND latest.max_ts = u.LastUpdatedDateAndTime
    ORDER BY u.FacilityName, u.LocationName
    """
    return sql_query(sql)


@mcp.tool()
def get_location(location_id):
    sql = """
    SELECT u.*
    FROM uwgyms u
    JOIN (
    SELECT LocationId, MAX(LastUpdatedDateAndTime) AS max_ts
    FROM uwgyms
    WHERE LocationId = %s
    GROUP BY LocationId
    ) latest
    ON latest.LocationId = u.LocationId
    AND latest.max_ts = u.LastUpdatedDateAndTime
    """
    return sql_query(sql, params=[location_id], limit=5)


@mcp.tool()
def least_busy_gym():
    sql = """
    SELECT u.LocationId,
        u.LocationName,
        u.FacilityName,
        u.CountOfParticipants,
        u.TotalCapacity,
        u.PercetageCapacity,
        u.LastUpdatedDateAndTime
    FROM uwgyms u
    JOIN (
    SELECT LocationId, MAX(LastUpdatedDateAndTime) AS max_ts
    FROM uwgyms
    GROUP BY LocationId
    ) latest
    ON latest.LocationId = u.LocationId
    AND latest.max_ts = u.LastUpdatedDateAndTime
    WHERE u.IsClosed = 0
    ORDER BY u.PercetageCapacity ASC, u.CountOfParticipants ASC
    LIMIT 1
    """
    return sql_query(sql)


@mcp.tool()
def debug_env():
    """
    debug env vars in setup
    """
    return {
        "UWB_DB_HOST": os.getenv("UWB_DB_HOST"),
        "UWB_DB_PORT": os.getenv("UWB_DB_PORT"),
        "UWB_DB_USER": os.getenv("UWB_DB_USER"),
        "UWB_DB_NAME": os.getenv("UWB_DB_NAME"),
    }


if __name__ == "__main__":
    mcp.run()