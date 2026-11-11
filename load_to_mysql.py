"""Midstone 4: load clean day 1 data into MySQL, then run queries.sql.
Midstone 4 — load your clean day 1 data into MySQL, then run your queries.

    python load_to_mysql.py          load the tables
    python load_to_mysql.py --run    load the tables, then run queries.sql into results/

Needs: pip install pandas sqlalchemy pymysql
Set MYSQL_USER and MYSQL_PASSWORD in your terminal first (see BRIEF.md).
Never write the password in this file.
"""
import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

HERE = Path(__file__).parent
DATA = HERE / "data"

MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
DATABASE = "fooddelivery"

if not MYSQL_PASSWORD:
    sys.exit("Set the MYSQL_PASSWORD environment variable first (see BRIEF.md).")

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{DATABASE}")

SOURCES = {
    "orders": HERE / "clean_orders.csv",  # your midstone 3 output
    "customers": DATA / "customers" / "customers.csv",
    "restaurants": DATA / "restaurants" / "restaurants.csv",
    "menu_items": DATA / "menu_items" / "menu_items.csv",
    "riders": DATA / "riders" / "riders.csv",
    "order_items": DATA / "order_items" / "day=01" / "order_items_01.csv",
    "payments": DATA / "payments" / "day=01" / "payments_01.csv",
}
TIME_COLUMNS = {"order_ts", "promised_ts", "delivered_ts", "updated_at", "payment_ts"}
MONEY_COLUMNS = {"total_amount", "price", "unit_price", "amount"}


def load(name, path):
    df = pd.read_csv(path, dtype=str)
    for col in TIME_COLUMNS & set(df.columns):
        df[col] = pd.to_datetime(df[col], format="%Y-%m-%d %H:%M:%S")
    for col in MONEY_COLUMNS & set(df.columns):
        df[col] = pd.to_numeric(df[col])
    df.to_sql(name, engine, if_exists="replace", index=False, chunksize=5000)
    print(f"loaded {name}: {len(df)} rows")


def run_queries():
    """Runs each query in queries.sql (separated by ';') and saves results/qN.csv."""
    sql = (HERE / "queries.sql").read_text(encoding="utf-8")
    statements = [s.strip() for s in sql.split(";") if s.strip() and not
                  all(line.strip().startswith("--") or not line.strip() for line in s.splitlines())]
    (HERE / "results").mkdir(exist_ok=True)
    with engine.connect() as conn:
        for n, statement in enumerate(statements, start=1):
            result = pd.read_sql(text(statement), conn)
            result.to_csv(HERE / "results" / f"q{n}.csv", index=False)
            print(f"q{n}: {len(result)} rows -> results/q{n}.csv")


for table, path in SOURCES.items():
    load(table, path)
if "--run" in sys.argv:
    run_queries()
