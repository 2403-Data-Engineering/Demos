// =============================================================
// Load smallsim.csv into Neo4j
//
// Graph model:
//   (:Account {id, type})  -[:TRANSACTION {step, type, amount, ...}]->  (:Account)
//
// Run in Neo4j Browser or cypher-shell.
// File must be in Neo4j's import directory (see notes below).
// =============================================================

// -------------------------------------------------------------
// 0. Optional cleanup — wipes existing data. Skip if you want to
//    keep what's there.
// -------------------------------------------------------------
MATCH (n) DETACH DELETE n;


// -------------------------------------------------------------
// 1. Constraint: ensures Account.id is unique. Also creates an
//    index automatically, which makes the MERGE in step 2 fast.
// -------------------------------------------------------------
CREATE CONSTRAINT account_id_unique IF NOT EXISTS
FOR (a:Account) REQUIRE a.id IS UNIQUE;


// -------------------------------------------------------------
// 2. Create Account nodes from unique nameOrig and nameDest values.
//    Type is derived from the ID prefix: C = customer, M = merchant.
// -------------------------------------------------------------
LOAD CSV WITH HEADERS FROM 'file:///smallsim.csv' AS row
MERGE (a:Account {id: row.nameOrig})
  ON CREATE SET a.type = CASE
    WHEN row.nameOrig STARTS WITH 'C' THEN 'customer'
    WHEN row.nameOrig STARTS WITH 'M' THEN 'merchant'
    ELSE 'unknown'
  END;

LOAD CSV WITH HEADERS FROM 'file:///smallsim.csv' AS row
MERGE (a:Account {id: row.nameDest})
  ON CREATE SET a.type = CASE
    WHEN row.nameDest STARTS WITH 'C' THEN 'customer'
    WHEN row.nameDest STARTS WITH 'M' THEN 'merchant'
    ELSE 'unknown'
  END;


// -------------------------------------------------------------
// 3. Create TRANSACTION relationships.
//    All transaction properties live on the edge.
//    toInteger / toFloat needed because LOAD CSV returns strings.
// -------------------------------------------------------------
LOAD CSV WITH HEADERS FROM 'file:///smallsim.csv' AS row
MATCH (orig:Account {id: row.nameOrig})
MATCH (dest:Account {id: row.nameDest})
CREATE (orig)-[t:TRANSACTION {
  step:           toInteger(row.step),
  type:           row.type,
  amount:         toFloat(row.amount),
  oldbalanceOrg:  toFloat(row.oldbalanceOrg),
  newbalanceOrig: toFloat(row.newbalanceOrig),
  oldbalanceDest: toFloat(row.oldbalanceDest),
  newbalanceDest: toFloat(row.newbalanceDest),
  isFraud:        toInteger(row.isFraud),
  isFlaggedFraud: toInteger(row.isFlaggedFraud)
}]->(dest);


// -------------------------------------------------------------
// 4. Sanity checks
// -------------------------------------------------------------
MATCH (a:Account) RETURN count(a) AS account_count;
MATCH ()-[t:TRANSACTION]->() RETURN count(t) AS transaction_count;
MATCH ()-[t:TRANSACTION]->() WHERE t.isFraud = 1 RETURN count(t) AS fraud_count;


// =============================================================
// NOTES
// =============================================================
//
// File location:
//   By default, Neo4j only loads CSVs from its `import` directory.
//   - Neo4j Desktop: right-click DB → Open folder → Import.
//     Drop smallsim.csv there.
//   - Docker: mount a volume to /var/lib/neo4j/import.
//   - To allow arbitrary paths, set in neo4j.conf:
//       dbms.security.allow_csv_import_from_file_urls=true
//       (not recommended for production)
//
// PROFILE / EXPLAIN:
//   Prefix any query with PROFILE to see the execution plan and
//   row counts at each step. Useful for debugging slow loads.
//
// Why MERGE not CREATE for accounts:
//   The same account ID appears many times across rows (as orig
//   AND dest). MERGE deduplicates — creates if missing, matches
//   if already present.
//
// Why CREATE not MERGE for transactions:
//   Each row is a distinct transaction event, even if the same
//   pair of accounts transacts repeatedly. We want every edge.
