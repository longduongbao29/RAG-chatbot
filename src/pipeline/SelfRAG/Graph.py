from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.language_models.chat_models import BaseChatModel
from langchain import hub
from pydantic import BaseModel, Field
from langgraph.graph import END, StateGraph, START

from src.rag.strategy.retrieval.RetrievalStrategy import RetrievalStrategy
from src.pipeline.ChatPipeline import ChatPipeline
from src.utils.logger import setup_logger
from src.pipeline.SelfRAG.State import GraphState
logger = setup_logger(__name__)

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )


class SelfRAG(ChatPipeline):    
    def __init__(self, **kwargs):
        self.name = "SelfRAG"
        self.description = "Self-Retrieval Augmented Generation Pipeline"
        self.llm: BaseChatModel = kwargs.get("llm") 
        self.retriever :RetrievalStrategy|None = kwargs.get("retriever")
        if self.retriever is None:
            raise ValueError("Retriever must be provided for SelfRAG pipeline.")
        if self.llm is None:
            raise ValueError("LLM must be provided for SelfRAG pipeline.")
        self.graph = self.build_graph()
    def retrieval_grader(self, question: str, doc_txt:str) -> GradeDocuments:
        """
        This method is a placeholder for the retrieval grading logic.
        It can be implemented to evaluate the quality of retrieved documents.
        """
        structured_llm_grader = self.llm.with_structured_output(GradeDocuments)

        # Prompt
        system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
            It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
            If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
        grade_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
            ]
        )

        retrieval_grader = grade_prompt | structured_llm_grader
        return retrieval_grader.invoke({"question": question, "document": doc_txt})
       
    def format_docs(self,docs):
            return "\n\n".join(doc.content for doc in docs)

    def llm_generate(self, question: str, documents: list):
        prompt = hub.pull("rlm/rag-prompt")
        rag_chain = prompt | self.llm | StrOutputParser()
        return rag_chain.invoke({"context": documents, "question": question})
    def hallucination_grader(self, documents: list, generation: str) -> GradeHallucinations:
        structured_llm_grader = self.llm.with_structured_output(GradeHallucinations)
        system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
        hallucination_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
            ]
        )

        hallucination_grader = hallucination_prompt | structured_llm_grader
        return hallucination_grader.invoke({"documents": documents, "generation": generation})
    def answer_grader(self, question: str, generation: str) -> GradeAnswer:
        structured_llm_grader = self.llm.with_structured_output(GradeAnswer)
        system = """You are a grader assessing whether an answer addresses / resolves a question \n 
     Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
            ]
        )

        answer_grader = answer_prompt | structured_llm_grader
        return answer_grader.invoke({"question": question, "generation": generation})
    def question_rewriter(self, question: str) -> str:
        """
        This method is a placeholder for the question rewriting logic.
        It can be implemented to refine or rephrase the user question.
        """
        # Example implementation could be added here
        system = """You a question re-writer that converts an input question to a better version that is optimized \n 
     for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
        re_write_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                (
                    "human",
                    "Here is the initial question: \n\n {question} \n Formulate an improved question.",
                ),
            ]
        )

        question_rewriter = re_write_prompt | self.llm | StrOutputParser()
        return question_rewriter.invoke({"question": question})

    ### Nodes


    def retrieve(self,state):
        """
        Retrieve documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        logger.info("---RETRIEVE---")
        question = state["question"]

        # Retrieval
        kargs = {
            "query": str(question),
            "collection_name": "default_collection",
            "search_type": "hybrid",
            "num_results": 5
        }
        documents = self.retriever.retrieve(**kargs)
        logger.info(f"Retrieved {len(documents)} documents.")
        return {"documents": documents, "question": question}


    def generate(self,state):
        """
        Generate answer

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """
        logger.info("---GENERATE---")
        question = state["question"]
        documents = state["documents"]

        # RAG generation
        generation = self.llm_generate(question, self.format_docs(documents))
        return {"documents": documents, "question": question, "generation": generation}


    def grade_documents(self,state):
        """
        Determines whether the retrieved documents are relevant to the question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates documents key with only filtered relevant documents
        """

        logger.info("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]

        # Score each doc
        filtered_docs = []
        for d in documents:
            score = self.retrieval_grader(question, d.content)
            grade = score.binary_score
            if grade == "yes":
                logger.info("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
            else:
                logger.info("---GRADE: DOCUMENT NOT RELEVANT---")
                continue
        return {"documents": filtered_docs, "question": question}


    def transform_query(self,state):
        """
        Transform the query to produce a better question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates question key with a re-phrased question
        """

        logger.info("---TRANSFORM QUERY---")
        question = state["question"]
        documents = state["documents"]

        # Re-write question
        better_question = self.question_rewriter(question)
        return {"documents": documents, "question": better_question}


    ### Edges


    def decide_to_generate(self,state):
        """
        Determines whether to generate an answer, or re-generate a question.

        Args:
            state (dict): The current graph state

        Returns:
            str: Binary decision for next node to call
        """

        logger.info("---ASSESS GRADED DOCUMENTS---")
        state["question"]
        filtered_documents = state["documents"]

        if not filtered_documents:
            # All documents have been filtered check_relevance
            # We will re-generate a new query
            logger.info(
                "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
            )
            return "transform_query"
        else:
            # We have relevant documents, so generate answer
            logger.info("---DECISION: GENERATE---")
            return "generate"


    def grade_generation_v_documents_and_question(self,state):
        """
        Determines whether the generation is grounded in the document and answers question.

        Args:
            state (dict): The current graph state

        Returns:
            str: Decision for next node to call
        """

        logger.info("---CHECK HALLUCINATIONS---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        score = self.hallucination_grader(documents, generation)
        grade = score.binary_score

        # Check hallucination
        if grade == "yes":
            logger.info("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
            # Check question-answering
            logger.info("---GRADE GENERATION vs QUESTION---")
            score = self.answer_grader(question, generation)
            grade = score.binary_score
            if grade == "yes":
                logger.info("---DECISION: GENERATION ADDRESSES QUESTION---")
                return "useful"
            else:
                logger.info("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
                return "not useful"
        else:
            logger.info("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
            return "not supported"
    def build_graph(self):
        workflow = StateGraph(GraphState)

        # Define the nodes
        workflow.add_node("retrieve", self.retrieve)  # retrieve
        workflow.add_node("grade_documents", self.grade_documents)  # grade documents
        workflow.add_node("generate", self.generate)  # generate
        workflow.add_node("transform_query", self.transform_query)  # transform_query

        # Build graph
        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges(
            "grade_documents",
            self.decide_to_generate,
            {
                "transform_query": "transform_query",
                "generate": "generate",
            },
        )
        workflow.add_edge("transform_query", "retrieve")
        workflow.add_conditional_edges(
            "generate",
            self.grade_generation_v_documents_and_question,
            {
                "not supported": "generate",
                "useful": END,
                "not useful": "transform_query",
            },
        )

        # Compile
        app = workflow.compile()

        return app
    def run(self, inputs: list) -> str:
        question ={"question": inputs[-1]} 
        for output in self.graph.stream(question):
            for key, value in output.items():
                logger.info(f"Node '{key}':")
                
            logger.info("\n---\n")
        return value["generation"]