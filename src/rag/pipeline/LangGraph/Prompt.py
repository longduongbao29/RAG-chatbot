from langchain_core.prompts import ChatPromptTemplate

# Template cho phân tích query
analyze_query_messages = [
    (
        "system",
        "You are an expert of analyzing the user input and decide which action to take:\n"
        "- retrive: Use this action when the user asks to find or retrieve information.\n"
        "- answer: Use this action for greetings, farewells, or any general conversational interaction that doesn't require knowledge retrieval."
    ),
    (
        "human",
        "Chat history: {history}\nUser input: {input}\nYour decision (retrive or answer):"
    )
]

ANALYZE_QUERY_PROMPT = ChatPromptTemplate(messages=analyze_query_messages)


# Template cho phân tích tool
analyze_tool_messages = [
    (
        "system",
        "You are an expert at analyzing user input and selecting the appropriate tools to retrieve information based on that analysis. "
        "You have access to the following tools:{list_tools}\n"
        "**Instructions:**\n\n"
        "1. **Analyze the User Input:**\n"
        "   Carefully review the query to identify key elements, such as time sensitivity or the need for real-time information.\n\n"
        "2. **Select the Appropriate Tools:**\n"
        "   - If the query involves real-time or current information, include **datetime_tool** to capture the current date/time context.\n"
        "   - For real-time data or news, follow up with **duckduckgo_search**.\n"
        "   - Always include **elastic_search** as the default tool for general knowledge-base searches if applicable.\n\n"
        "3. **List the Tools in Order:**\n"
        "   Provide a list of the tools in the exact order they should be used to fulfill the query.\n\n"
        "4. **Explain Your Reasoning:**\n"
        "   Include a brief explanation of why each tool was selected based on the query.\n\n"
        "**Examples:**\n\n"
        "- **User Input:** \"What is the weather like today?\"\n"
        "  **Reasoning:** The query asks for current weather information. Therefore, use **datetime_tool** to determine the current date/time, followed by **duckduckgo_search** for real-time weather data.\n"
        "  **Analysis (tools to use):** `[datetime_tool, duckduckgo_search]`\n\n"
        "- **User Input:** \"Search for the latest news?\"\n"
        "  **Reasoning:** The query asks for the latest news, which is time-sensitive. First, use **datetime_tool** to obtain the current context, then use **duckduckgo_search** to retrieve the latest news.\n"
        "  **Analysis (tools to use):** `[datetime_tool, duckduckgo_search]`"
    ),
    (
        "human",
        "Now, process the following user input: {input}\n"
        "Do not provide any explanations for your answers, just return the list of tools.\n"
        "**Analysis (tools to use):**"
    )
]

ANALYZE_TOOL_PROMPT = ChatPromptTemplate(messages=analyze_tool_messages)


# Template cho RAG
rag_messages = [
    (
        "system",
        "You are a helpful assistant that can answer questions based on the given context. "
        "You should use the provided context to answer the question. "
        "Do not provide any explanations for your answers."
    ),
    (
        "human",
        "Context: {context}\nHistory chat: {history}Question: {query}\n"
    )
]

RAG_PROMPT = ChatPromptTemplate(messages=rag_messages)

def getPromptWithInstruction(instruction:str):
    messages = [(
        "system",
        "You are a helpful assistant that can answer questions based on the given context. "
        "You should use the provided context to answer the question. "
        "Do not provide any explanations for your answers."
        f"Instruction: {instruction}"
    ),
    (
        "human",
        "Context: {context}\nHistory chat: {history}Question: {query}\n"
    )]
    return ChatPromptTemplate(messages=messages)
