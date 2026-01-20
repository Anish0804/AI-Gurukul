from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = FAISS.load_local(
    "faiss_index",
    embedding,
    allow_dangerous_deserialization=True
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})


def get_rag_context(query: str) -> str:
    """
    Returns reference context ONLY.
    No DB values. No decisions.
    """
    docs = retriever.invoke(query)
    

    context_blocks = []
    for d in docs:
        source = d.metadata.get("source", "unknown")
        context_blocks.append(
            f"\n--- Reference from {source} ---\n{d.page_content}"
        )

    return "\n".join(context_blocks)
