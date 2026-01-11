from langchain_community.llms import Ollama
import json

llm = Ollama(
    model="gemma3:4b",
    base_url="http://localhost:11434"
)

def summarize(tool_name: str, tool_output: dict) -> str:
        prompt = f"""
    Tool used: {tool_name}

    Tool output:
    {json.dumps(tool_output, indent=2)}

    Explain this clearly to the user in plain English.
    """
        return llm.invoke(prompt)
