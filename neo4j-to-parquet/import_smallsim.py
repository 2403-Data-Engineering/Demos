"""
Load smallsim.csv into Neo4j as a graph.

Graph model:
  (:Account {id, type})  -[:TRANSACTION {step, type, amount, ...}]->  (:Account)

Same model as load_smallsim.cypher, but driven from Python so no need
to copy the CSV into Neo4j's import folder.
"""

import csv
from pathlib import Path
from neo4j import GraphDatabase

# -------------------------------------------------------------
# Config
# -------------------------------------------------------------
NEO4J_URI      = "bolt://localhost:7687"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "password"   # change to match your DB

CSV_PATH = Path("./Smallsim_CSV/smallsim.csv")
BATCH_SIZE = 500              # rows per write transaction


# -------------------------------------------------------------
# Cypher fragments
# -------------------------------------------------------------
WIPE = "MATCH (n) DETACH DELETE n"

CREATE_CONSTRAINT = """
CREATE CONSTRAINT account_id_unique IF NOT EXISTS
FOR (a:Account) REQUIRE a.id IS UNIQUE
"""

# UNWIND lets us send a batch of rows in a single query — much faster
# than one query per row.
MERGE_ACCOUNTS = """
UNWIND $rows AS row
MERGE (a:Account {id: row.id})
  ON CREATE SET a.type = row.type
"""

CREATE_TRANSACTIONS = """
UNWIND $rows AS row
MATCH (orig:Account {id: row.nameOrig})
MATCH (dest:Account {id: row.nameDest})
CREATE (orig)-[:TRANSACTION {
  step:           row.step,
  type:           row.type,
  amount:         row.amount,
  oldbalanceOrg:  row.oldbalanceOrg,
  newbalanceOrig: row.newbalanceOrig,
  oldbalanceDest: row.oldbalanceDest,
  newbalanceDest: row.newbalanceDest,
  isFraud:        row.isFraud,
  isFlaggedFraud: row.isFlaggedFraud
}]->(dest)
"""


def account_type(account_id: str) -> str:
    if account_id.startswith("C"):
        return "customer"
    if account_id.startswith("M"):
        return "merchant"
    return "unknown"


def chunked(iterable, size):
    """Yield successive chunks of `size` from iterable."""
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def main():
    print(f"Reading {CSV_PATH}...")
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"  {len(rows)} transactions in CSV")

    # Build deduplicated account list from origin and destination columns
    account_map = {}
    for row in rows:
        for col in ("nameOrig", "nameDest"):
            acct = row[col]
            if acct not in account_map:
                account_map[acct] = {"id": acct, "type": account_type(acct)}
    accounts = list(account_map.values())
    print(f"  {len(accounts)} unique accounts derived")

    # Coerce types up front so the Cypher doesn't have to (faster than toFloat in query)
    txn_rows = [
        {
            "nameOrig":       r["nameOrig"],
            "nameDest":       r["nameDest"],
            "step":           int(r["step"]),
            "type":           r["type"],
            "amount":         float(r["amount"]),
            "oldbalanceOrg":  float(r["oldbalanceOrg"]),
            "newbalanceOrig": float(r["newbalanceOrig"]),
            "oldbalanceDest": float(r["oldbalanceDest"]),
            "newbalanceDest": float(r["newbalanceDest"]),
            "isFraud":        int(r["isFraud"]),
            "isFlaggedFraud": int(r["isFlaggedFraud"]),
        }
        for r in rows
    ]

    print(f"Connecting to {NEO4J_URI}...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        print("Wiping existing data...")
        session.run(WIPE)

        print("Creating uniqueness constraint...")
        session.run(CREATE_CONSTRAINT)

        print(f"Creating accounts (batches of {BATCH_SIZE})...")
        for batch in chunked(accounts, BATCH_SIZE):
            session.run(MERGE_ACCOUNTS, rows=batch)

        print(f"Creating transactions (batches of {BATCH_SIZE})...")
        for i, batch in enumerate(chunked(txn_rows, BATCH_SIZE), start=1):
            session.run(CREATE_TRANSACTIONS, rows=batch)
            print(f"  batch {i}: {len(batch)} transactions")

        # Sanity checks
        print("\nVerifying...")
        n_accounts = session.run("MATCH (a:Account) RETURN count(a) AS c").single()["c"]
        n_txns     = session.run("MATCH ()-[t:TRANSACTION]->() RETURN count(t) AS c").single()["c"]
        n_fraud    = session.run("MATCH ()-[t:TRANSACTION]->() WHERE t.isFraud = 1 RETURN count(t) AS c").single()["c"]
        print(f"  Accounts:     {n_accounts}")
        print(f"  Transactions: {n_txns}")
        print(f"  Fraud:        {n_fraud}")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()