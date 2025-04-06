from langchain_core.prompts import ChatPromptTemplate

analyze_query_prompt = """
You are an expert of analyzing the user input and decide which action to take:
- retrive: Use this action when the user asks to find or retrieve information.
- answer: Use this action for greetings, farewells, or any general conversational interaction that doesn't require knowledge retrieval.

User input: {input}
Your decision (retrive or answer): 
"""

ANALYZE_QUERY_PROMPT = ChatPromptTemplate.from_template(analyze_query_prompt)

analyze_tool_prompt = """
You are an expert of analyzing the user input and choose which tool should be used to retrieve information base on the analysis.
Below are some tools that you can use to analyze the user input:
- elastic_search: search the knowledge base from elastic_database. Always use this tool as defaut.
- duckduckgo_search: search the information online, use this tool to search realtime information.
- datetime_tool : if query involve current, today, at the moment... use this tool to provide the datetime context.

You can use more than one tool.
List tools must be in using order.

###
Example:
User input: What is the wearther like today?
Resoning: The user is asking for the current weather, which is a realtime information. So I will use date_time_tool to get current date time, after that use duckduckgo_search to search the web for the current weather.
Analysis (tools to use): [date_time_tool, duckduckgo_search]

User input: Search for the latest news?
Resoning: The user is asking for the latest news, which is a realtime information. So I will use date_time_tool to get current date time, after that use duckduckgo_search to search the web for the latest news.
Analysis (tools to use): [date_time_tool, duckduckgo_search]

###


User input: {input}
Analysis (tools to use):
"""

ANALYZE_TOOL_PROMPT = ChatPromptTemplate.from_template(analyze_tool_prompt)

rag_promt = """You are a helpful assistant that can answer questions based on the given context.
You should use the provided context to answer the question. 
If you don't know the answer, just say that you don't know. 
Do not provide any explanations for your answers.
Question: {query}
Context: {context}
"""
RAG_PROMPT = ChatPromptTemplate.from_template(rag_promt)