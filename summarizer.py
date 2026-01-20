from langchain_community.llms import Ollama
import json

llm = Ollama(
    model="gemma3:4b",
    base_url="http://localhost:11434"
)

def summarize(tool_name, tool_result, rag_context, user_question):
    prompt = f"""
You are a banking assistant.

CRITICAL RULES:
1. ALL factual information (names, balances, dates, amounts, transactions)
   MUST come ONLY from the tool response.
2. Reference material is for explanation or formatting ONLY.
3. NEVER copy, infer, or guess values from reference material.
4. If a value is missing in the tool response, say:
   "This information is not available."
5. If the question is unrelated to banking, reply:
   "Sorry, I can only help with banking-related queries."

User Question:
{user_question}

Tool Response (AUTHORITATIVE FACTS):
{tool_result}

Reference Material (DO NOT USE AS DATA):
{rag_context}

Answer clearly and professionally.
"""

    return llm.invoke(prompt)
