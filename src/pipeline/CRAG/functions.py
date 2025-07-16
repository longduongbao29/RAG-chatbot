
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models.base import BaseChatModel
from langchain import hub
from langchain_core.output_parsers import StrOutputParser

from src.rag.strategy.retrieval.OnlineSearch import OnlineSearch
from src.pipeline.CRAG.models import GradeDocuments
from src.utils.Document import Document

def grade_documents(llm: BaseChatModel, question: str, doc: Document) -> GradeDocuments:
    structured_llm_grader = llm.with_structured_output(GradeDocuments)
    # Prompt
    system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
        If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
        ]
    )

    retrieval_grader = grade_prompt | structured_llm_grader
    return retrieval_grader.invoke({"question": question, "document": doc.content})

def format_docs(docs:list[Document], history) -> str:
    docs_txt =  "\n\n".join(doc.content for doc in docs)
    context = f"""
Current conversation:
{history}
Retrieve infomations:
{docs_txt}
    """
    return context

def llm_generate(llm: BaseChatModel, question: str, docs: str) -> str:
    prompt = hub.pull("rlm/rag-prompt")
    rag_chain = prompt | llm | StrOutputParser()
    return rag_chain.invoke({"context": docs, "question": question})

def rewrite_query(llm: BaseChatModel, question: str) -> str:
    system = """You a question re-writer that converts an input question to a better version that is optimized \n 
     for web search. Look at the input and try to reason about the underlying semantic intent / meaning."""
    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Here is the initial question: \n\n {question} \n Formulate an improved question. Return only the question without any additional text.",
            ),
        ]
    )

    question_rewriter = re_write_prompt | llm | StrOutputParser()
    return question_rewriter.invoke({"question": question})

def web_search(web_search: OnlineSearch, question: str) -> str:
    """
    Perform a web search using the provided retrieval strategy.
    """
    return web_search.search(question)


