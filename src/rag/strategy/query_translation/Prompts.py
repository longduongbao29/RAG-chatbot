from langchain_core.prompts import ChatPromptTemplate

rag_fusion_messages = [
    (
        "system",
        "You are an advanced query translator in a Retrieval-Augmented Generation system. Your task is to take a complex user query and break it down into its key components. For each component, generate a subquery that focuses on a distinct aspect of the information needed. Then, fuse these subqueries into one coherent, composite query that preserves the original intent and maximizes the relevance of the retrieved context."
    ),
    (
        "human",
        "User Query: {query}\nHistory Chat: {history}\n\nSteps:\n1. Identify the key themes or components of the query.\n2. For each theme, produce a subquery that captures its essence.\n3. Combine these subqueries using logical operators (e.g., AND, OR) to create a final fused query.\n\nDo not include any explanations or additional text in the output. Just provide the subqueries and the final fused query.\n\nOutput format:\n{{queries:[Query1, Query2, Query3, Query4, Query5]}}\n\nOutput (5 queries):"
    )
]

RAG_FUSION_PROMPT = ChatPromptTemplate(messages=rag_fusion_messages)
