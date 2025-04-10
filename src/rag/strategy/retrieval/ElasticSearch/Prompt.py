from langchain_core.prompts import ChatPromptTemplate

index_name_messages = [
    (
        "system",
        "You are an expert at analyzing the user input and choose which indexes should be used to retrieve information based on the analysis. "
        "There would be multiple indexes involved. "
        "If the user input is not related to any of the provided indexes, return []."
    ),
    (
        "human",
        "Index descriptions: {index_descriptions}\nUser input: {input}\nAnalysis (list indexes to use):"
    )
]

INDEX_NAME_TEMPLATE = ChatPromptTemplate(messages=index_name_messages)
