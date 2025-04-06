from langchain_core.prompts import ChatPromptTemplate

index_name_template = """You are an expert at analyzing the user input and choose which index should be used to retrieve information base on the analysis.
User input: {input}
Index descriptions: {index_descriptions}
If the user input is not related to any of the provided indexes, return None.
Analysis (index to use|None):"""

INDEX_NAME_TEMPLATE = ChatPromptTemplate.from_template(
    template=index_name_template    
)