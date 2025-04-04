from langchain_core.prompts import ChatPromptTemplate

rag_fusion_prompt = """You are an advanced query translator in a Retrieval-Augmented Generation system. Your task is to take a complex user query and break it down into its key components. For each component, generate a subquery that focuses on a distinct aspect of the information needed. Then, fuse these subqueries into one coherent, composite query that preserves the original intent and maximizes the relevance of the retrieved context.

User Query: {query}
Steps:

1.Identify the key themes or components of the query.
2.For each theme, produce a subquery that captures its essence.
3.Combine these subqueries using logical operators (e.g., AND, OR) to create a final fused query.

Output the final fused query along with a brief explanation of each subquery’s role.(5 queries)"""

RAG_FUSION_PROMPT = ChatPromptTemplate.from_template(
    template=rag_fusion_prompt,
)