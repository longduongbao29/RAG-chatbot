from abc import ABC, abstractmethod

from pydantic import BaseModel, Field  
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import PromptTemplate

from src.rag.strategy.retrieval.Prompts.rerank_prompts import default_rerank_prompt
from src.utils.Document import Document
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class Reranker(ABC):
    """
    Abstract base class for rerankers.
    """
    def __init__(self):
        """
        Initialize the reranker.
        """
    @abstractmethod
    def rerank(self, doc_lists: list[Document], topk=5) -> list[Document]:
        """
        Rerank the documents based on some criteria.
        """
        pass
class RankingOutput(BaseModel):  
    '''An answer to the user question along with justification for the answer.'''  
    ranking_order: list[int] = Field(description="List of passage identifiers in descending order of relevance to the query.", default=[])

class LLMReranker(Reranker):
    """
    LLM-based reranker for documents.
    """
    def __init__(self, llm: BaseChatModel, prompt : PromptTemplate = default_rerank_prompt):
        """
        Initialize the LLM reranker with a language model.
        """
        super().__init__()
        self.llm = llm.with_structured_output(RankingOutput)
        self.prompt = prompt

    def rerank(self, doc_lists: list[Document], query:str, topk=5):
        """
        Rerank the documents using the LLM.
        """
        input = {
            "n": len(doc_lists),
            "query": query,
            "passages": [doc.content for doc in doc_lists]
        }
        chain = input | self.prompt | self.llm

        rank: RankingOutput = chain.invoke(input)
        if not rank.ranking_order:
            logger.warning("Reranker returned an empty ranking order. Returning original document list.")
            return doc_lists[:topk]
        rerank_doc_lists = [doc_lists[i - 1] for i in rank.ranking_order if i <= len(doc_lists)]

        return rerank_doc_lists[:topk]  

class RRFReranker(Reranker):
    """
    Reciprocal Rank Fusion (RRF) reranker for documents.
    """
    def __init__(self):
        """
        Initialize the RRF reranker.
        """
        super().__init__()

    def rerank(self, doc_lists: list[list[Document]], topk=5):
        """
        Rerank the retrieved documents based on relevance.
        """
        # Implement reranking logic here
        docs_with_rank:list[tuple[Document,float]] = []
        
        for doc_list in doc_lists:
            for d in doc_list:
                if any(d.id == doc[0].id for doc in docs_with_rank):
                    continue
                rank = self.reciprocal_rank_fusion(d, 10, doc_lists)
                docs_with_rank.append((d, rank))

        docs_with_rank.sort(key=lambda x: x[1], reverse=True)
        return [dwr[0] for dwr in docs_with_rank][:topk]

    def rank_func(self,results:list[Document], d:Document):
        index = -1
        for i, doc in enumerate(results):
            if doc.id == d.id:
                index = i
                break
        return index + 1

    
    def reciprocal_rank_fusion(self,d: Document, k:int, list_docs:list[list[Document]]) -> float:
        sum = 0
        for list_doc in list_docs:
            rank_f = self.rank_func(list_doc, d)
            if rank_f > 0:
                sum += 1.0 / (k + rank_f)
        return sum