from langchain_core.prompts import ChatPromptTemplate

analyze_query_prompt = """
You are an expert of analyzing the user input and decide which action to take:
- retrive: Use this action when the user asks to find or retrieve information.
- answer: Use this action for greetings, farewells, or any general conversational interaction that doesn't require knowledge retrieval.

User input: {input}
Chat history: {history}
Your decision (retrive or answer): 
"""

ANALYZE_QUERY_PROMPT = ChatPromptTemplate.from_template(analyze_query_prompt)

analyze_tool_prompt = """You are an expert at analyzing user input and selecting the appropriate tools to retrieve information based on that analysis. You have access to the following tools:
- **elastic_search**: Searches the knowledge base using an elastic database. This is the default tool.
- **duckduckgo_search**: Searches online for real-time information.
- **datetime_tool**: Provides the current date and time when the query involves terms like "today," "current," "now," etc.

**Instructions:**

1. **Analyze the User Input:**  
   Carefully review the query to identify key elements, such as time sensitivity or the need for real-time information.

2. **Select the Appropriate Tools:**  
   - If the query involves real-time or current information, include **datetime_tool** to capture the current date/time context.  
   - For real-time data or news, follow up with **duckduckgo_search**.  
   - Always include **elastic_search** as the default tool for general knowledge-base searches if applicable.

3. **List the Tools in Order:**  
   Provide a list of the tools in the exact order they should be used to fulfill the query.

4. **Explain Your Reasoning:**  
   Include a brief explanation of why each tool was selected based on the query.

**Examples:**

- **User Input:** "What is the weather like today?"  
  **Reasoning:** The query asks for current weather information. Therefore, use **datetime_tool** to determine the current date/time, followed by **duckduckgo_search** for real-time weather data.  
  **Analysis (tools to use):** `[datetime_tool, duckduckgo_search]`

- **User Input:** "Search for the latest news?"  
  **Reasoning:** The query asks for the latest news, which is time-sensitive. First, use **datetime_tool** to obtain the current context, then use **duckduckgo_search** to retrieve the latest news.  
  **Analysis (tools to use):** `[datetime_tool, duckduckgo_search]`

**Your Task:**

Now, process the following user input: {input}
**Analysis (tools to use):**
"""

ANALYZE_TOOL_PROMPT = ChatPromptTemplate.from_template(analyze_tool_prompt)

rag_promt = """You are a helpful assistant that can answer questions based on the given context.
You should use the provided context to answer the question. 
If you don't know the answer, just say that you don't know. 
Do not provide any explanations for your answers.
Question: {query}
Context: {context}
History chat: {history}
"""
RAG_PROMPT = ChatPromptTemplate.from_template(rag_promt)