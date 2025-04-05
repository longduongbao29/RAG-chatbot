from langchain_core.prompts import ChatPromptTemplate

analyze_query_prompt = """
You are an expert of analyzing the user input and decide which action to take:
- retrive: retrieve more information from the knowledge base if you dont know.
- answer: answer the question directly.

User input: {input}
Your decision (retrive or answer): 
"""

ANALYZE_QUERY_PROMPT = ChatPromptTemplate.from_template(analyze_query_prompt)

analyze_tool_prompt = """
You are an expert of analyzing the user input and choose which tool should be used to retrieve information base on the analysis.
Below are some tools that you can use to analyze the user input:
- duckduckgo_search: search the web for information, use this tool to search realtime information.
- elastic_search: search the knowledge base for information: NameA, NameB, Virruss drama.
- datetime_tool : use this tool to get the curent date and time.

You can use more than one tool or decide no tools will be used.
###
Example:
User input: What is the wearther like today?
Resoning: The user is asking for the current weather, which is a realtime information. So I will use date_time_tool to get current date time, after that use duckduckgo_search to search the web for the current weather.
Analysis (tools to use): [date_time_tool, duckduckgo_search]
###

List tools must be in using order.

User input: {input}
Analysis (tools to use):
"""

ANALYZE_TOOL_PROMPT = ChatPromptTemplate.from_template(analyze_tool_prompt)

rag_promt = """You are a helpful assistant that can answer questions based on the given context.
Question: {query}
Context: {context}
"""
RAG_PROMPT = ChatPromptTemplate.from_template(rag_promt)