import json
from langchain_community.llms import Ollama
import re

llm = Ollama(
    model="gemma3:4b",
    base_url="http://localhost:11434"
)

TOOLS = {
    "get_account_balance": ["account_id"],
    "get_transaction_history": ["account_id"],
    "get_adhoc_statements": ["account_id"],
    "get_periodic_statements": ["account_id"],
}
def extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```json|```$", "", text, flags=re.MULTILINE).strip()
    return text

def plan_tool_call(user_message: str) -> dict:
    prompt = f"""
    You are a banking assistant.

    Decide what to do with the user's message.

    Rules:
    - If the question requires bank data, return a TOOL call
    - If it is casual or informational, return CHAT
    - If it is unrelated to banking (food, sports, politics), return REJECT

    Available tools:
    - get_account_balance(account_id)
    - get_transaction_history(account_id)
    - get_adhoc_statements(account_id)
    - get_periodic_statements(account_id)

    Return ONLY valid JSON in one of these formats.

    TOOL:
    {{ "type": "tool", "tool": "...", "args": {{...}} }}

    CHAT:
    {{ "type": "chat", "response": "..." }}

    REJECT:
    {{ "type": "reject", "response": "..." }}

    User message:
    \"\"\"{user_message}\"\"\"
    """

    response = llm.invoke(prompt).strip()
    cleaned = extract_json(response)
    print("RAW LLM RESPONSE:")
    print(repr(response))

    if not response or not response.strip():
        raise ValueError("LLM returned empty response")

    return json.loads(cleaned)
