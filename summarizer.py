from langchain_community.llms import Ollama
import json

llm = Ollama(
    model="gemma3:4b",
    base_url="http://localhost:11434"
)

def summarize(tool_name, tool_result, rag_context):
    prompt = f"""
You are a banking assistant.

Authoritative data (from database):
{tool_result}

Reference material (for explanation/format only):
{rag_context}

Rules:
- Do NOT invent values
- DB values override everything
- Use reference only for explanation
"""

    return llm.invoke(prompt)

