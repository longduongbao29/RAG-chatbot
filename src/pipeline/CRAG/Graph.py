from langchain.chat_models.base import BaseChatModel
from langgraph.graph import END, StateGraph, START

from src.rag.strategy.retrieval.RetrievalStrategy import RetrievalStrategy
from src.pipeline.ChatPipeline import ChatPipeline
from src.pipeline.CRAG.functions import (
    grade_documents,
    format_docs,
    llm_generate,
    rewrite_query,
    web_search,)
from src.pipeline.CRAG.models import GradeDocuments
from src.pipeline.CRAG.states import GraphState
from src.utils.Document import Document
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CRAG(ChatPipeline):
    name = "CRAG"
    description = "CRAG is a pipeline that processes and analyzes data using langchain graph."
    
    def __init__(self,llm : BaseChatModel, db_retriever: RetrievalStrategy, web_search_retriever: RetrievalStrategy):
        self.llm = llm
        self.db_retriever = db_retriever
        self.web_serch_retriever = web_search_retriever
        self.app = self.build_graph()

    def run(self, inputs) -> str:
        """
        Run the CRAG pipeline.

        Returns:
            dict: The final state of the pipeline after processing.
        """
        ips = {
            "conversation": inputs
            }
        for output in self.app.stream(ips):
            for key, value in output.items():
                # Node
                logger.info(f"Node '{key}':")
                # Optional: logger.info full state at each node
                # logger.info.logger.info(value["keys"], indent=2, width=80, depth=None)
            logger.info("\n---\n")

        # Final generation
        return value["generation"]
    def retrieve(self,state):
        """
        Retrieve documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        logger.info("---RETRIEVE---")
        logger.info([state["conversation"]])
        question = state["conversation"][-1]["message"]
        # Retrieval
        inputs = {"query": str(question)}
        documents = self.db_retriever.retrieve(**inputs)
        return {"documents": documents, "conversation": state["conversation"]}


    def generate(self,state):
        """
        Generate answer

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """
        logger.info("---GENERATE---")
        question = state["conversation"][-1]["message"]
        documents = state["documents"]
        history  = state["conversation"][:-1]
        # RAG generation
        generation = llm_generate(self.llm, question, format_docs(documents, history))
        return {"documents": documents, "conversation": state["conversation"], "generation": generation}


    def grade_documents(self,state):
        """
        Determines whether the retrieved documents are relevant to the question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates documents key with only filtered relevant documents
        """

        logger.info("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["conversation"][-1]["message"]
        documents: list[Document] = state["documents"]

        # Score each doc
        filtered_docs = []
        web_search = "No"
        for d in documents:
            score: GradeDocuments = grade_documents(
                llm=self.llm, question=question, doc=d
            )
            grade = score.binary_score
            if grade == "yes":
                logger.info("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
            else:
                logger.info("---GRADE: DOCUMENT NOT RELEVANT---")
                web_search = "Yes"
                continue
        return {"documents": filtered_docs, "conversation": state["conversation"], "web_search": web_search}


    def transform_query(self,state):
        """
        Transform the query to produce a better question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates question key with a re-phrased question
        """

        logger.info("---TRANSFORM QUERY---")
        question = state["conversation"][-1]["message"]
        documents = state["documents"]

        # Re-write question
        better_question = rewrite_query(llm = self.llm, question=question)
        state["conversation"][-1]["message"] = better_question
        return {"documents": documents, "conversation": state["conversation"]}


    def web_search(self,state):
        """
        Web search based on the re-phrased question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates documents key with appended web results
        """

        logger.info("---WEB SEARCH---")
        question = state["conversation"][-1]["message"]
        documents = state["documents"]

        # Web search
        search_result = self.web_serch_retriever.retrieve(query=question)
       
        web_results = Document(id = "web-search",content=search_result)
        logger.info(f"Web search for question: {question}")
        logger.info(f"Web search results: \n{web_results.content}")
        documents.append(web_results)

        return {"documents": documents, "conversation": state["conversation"]}


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
        web_search = state["web_search"]

        if web_search == "Yes":
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
        
    def build_graph(self):
        """
        Build the graph of the pipeline.

        Returns:
            dict: The graph structure of the pipeline
        """
        workflow = StateGraph(GraphState)

        # Define the nodes
        workflow.add_node("retrieve", self.retrieve)  # retrieve
        workflow.add_node("grade_documents", self.grade_documents)  # grade documents
        workflow.add_node("generate", self.generate)  # generate
        workflow.add_node("transform_query", self.transform_query)  # transform_query
        workflow.add_node("web_search_node", self.web_search)  # web search

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
        workflow.add_edge("transform_query", "web_search_node")
        workflow.add_edge("web_search_node", "generate")
        workflow.add_edge("generate", END)

        # Compile
        app = workflow.compile()
        return app