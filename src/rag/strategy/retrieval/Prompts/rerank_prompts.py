from langchain_core.prompts import ChatPromptTemplate

rerank_template = """System: You are RankLlama, an intelligent assistant that can rank passages based on their relevancy to the query.
User: I will provide {n} passages, numbered [1]–[{n}]. Please rank them in descending order of relevance to the query: {query}.
Passages: {passages}
List identifiers in descending order:
"""

default_rerank_prompt = ChatPromptTemplate.from_template(rerank_template)