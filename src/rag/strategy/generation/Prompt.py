from langchain_core.prompts import ChatPromptTemplate

gen_prompt = """You are an expert assistant. Use the provided context to answer the question accurately.

### Context:
{context}

### Question:
{query}

### Answer:"""
GEN_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
    template=gen_prompt,
)