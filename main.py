from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from langchain_community.llms import Ollama
from rag_service import get_rag_context

from planner import plan_tool_call
#from mcp_client import call_mcp_tool
from summarizer import summarize
from tool_executor import execute_tool
import sqlite3

import json

DB_NAME = "AIGurukul.db"

'''from mcp_tools import (
    get_account_balance,
    get_transaction_history,
    get_adhoc_statements,
    get_periodic_statements,
)



tools = [
    get_account_balance,
    get_transaction_history,
    get_adhoc_statements,
    get_periodic_statements,
]'''

app = FastAPI()

llm = Ollama(
    model="gemma3:4b",
    base_url="http://localhost:11434"
)
'''agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)'''

'''agent = create_agent(
    llm=llm,
    tools=tools,
    agent_type="react",   # ReAct reasoning
    verbose=True,
)'''

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---- Hardcoded users ----
USERS = {
    "anish": "password123",
    "admin": "admin123",
    "guest": "guest123"
}


class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str

# ---- Routes ----
@app.post("/login")
def login(req: LoginRequest):
    if req.username not in USERS or USERS[req.username] != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"status": "success"}

# ADDED THIS NEW ENDPOINT HERE
@app.get("/welcome")
def get_welcome_message():
    return {
        "message": "Hi, I am your banking assistant. How can I help you today?",
        "status": "ready"
    }

'''@app.post("/chat")
def chat(req: ChatRequest):
    response = llm.invoke(req.message)
    return {"response": response}'''
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

'''@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = llm.invoke(req.message)
    return {"response": result}
'''
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
'''

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

'''@app.post("/chat")
def chat(req: ChatRequest):
    response = agent.run(req.message)
    return {"response": response}'''
'''@app.post("/chat")
def chat(req: ChatRequest):
    result = agent.invoke(
        {"input": req.message}
    )
    return {"response": result["output"]}'''

from tool_executor import execute_tool

@app.post("/chat")
def chat(req: ChatRequest):
    plan = plan_tool_call(req.message)

    if plan["type"] == "tool":
        tool_result = execute_tool(plan["tool"], plan["args"])
        rag_context = get_rag_context("bank statement format transaction explanation")
        
        final_answer = summarize(tool_name=plan["tool"],tool_result=tool_result,rag_context=rag_context)
        return {"response": final_answer}

    elif plan["type"] == "chat":
        return {"response": plan["response"]}

    elif plan["type"] == "reject":
        return {"response": plan["response"]}

    else:
        return {"response": "Unable to process request."}
