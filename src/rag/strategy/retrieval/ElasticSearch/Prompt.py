from langchain_core.prompts import ChatPromptTemplate

index_name_template = """You are an expert at analyzing the user input and choose which indexs should be used to retrieve information base on the analysis.
User input: {input}
Index descriptions: {index_descriptions}
There would be multiple indexs involved.
If the user input is not related to any of the provided indexes, return [].
Analysis (list indexs to use):"""

INDEX_NAME_TEMPLATE = ChatPromptTemplate.from_template(
    template=index_name_template    
)