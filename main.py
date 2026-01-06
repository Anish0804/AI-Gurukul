from fastapi import FastAPI, HTTPException
import sqlite3

app = FastAPI(title="AIGurukul Banking APIs")

DB_NAME = "AIGurukul.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# 1️⃣ Account Balance
@app.get("/api/accounts/{account}/balance")
def get_account_balance(account: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT accountId, balanceAmount, currency, asOfDate
        FROM AccountBalance
        WHERE accountId = ?
        ORDER BY asOfDate DESC
        LIMIT 1
    """, (account,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Account not found")

    return dict(row)


# 2️⃣ Balance History -> not sure on how to generate and what to generate yet, so commenting the function for the timebeing
'''@app.get("/api/accounts/{account}/balance/history")
def get_balance_history(account: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT txnDate, balanceAfterTxn
        FROM TransactionHistory
        WHERE accountId = ?
        ORDER BY txnDate ASC
    """, (account,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "accountId": account,
        "balanceHistory": [dict(row) for row in rows]
    }


# 3️⃣ Transaction History
@app.get("/api/accounts/{account}/transactions")
def get_transaction_history(account: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transactionId, date, description, netAmount, type, "balance After"
        FROM TransactionHistory
        WHERE accountId = ?
        ORDER BY date DESC
    """, (account,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "accountId": account,
        "transactions": [dict(row) for row in rows]
    }
'''

# 4️⃣ AdHoc Statements
@app.get("/api/accounts/{account}/statements/adhoc")
def get_adhoc_statements(account: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT statementId, startDate, endDate, requestId,
               submittedByRole, requestTimestamp
        FROM AdHocStatement
        WHERE accountId = ?
        ORDER BY requestTimestamp DESC
    """, (account,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "accountId": account,
        "adhocStatements": [dict(row) for row in rows]
    }


# 5️⃣ Periodic (Current) Statements
@app.get("/api/accounts/{account}/statements/current")
def get_periodic_statements(account: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT accountId, periodStartDate, periodEndDate, OpeningBalance, ClosingBalance
        FROM PeriodicStatement
        WHERE accountId = ?
        ORDER BY periodEndDate DESC
    """, (account,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "accountId": account,
        "periodicStatements": [dict(row) for row in rows]
    }
