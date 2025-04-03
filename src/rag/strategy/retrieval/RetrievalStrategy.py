from abc import ABC, abstractmethod
from pydoc import doc


from rag.strategy.retrieval.Document import Document

class RetrievalStrategy(ABC):
    """
    Abstract base class for retrieval strategies.
    """
    @abstractmethod
    def retrieve(self, query):
        """
        Retrieve documents based on the query.
        """
        pass
    def rerank(self, doc_lists: list[list[Document]], topk=5):
        """
        Rerank the retrieved documents based on relevance.
        """
        # Implement reranking logic here
        docs_with_rank:list[tuple[Document,float]] = []
        
        for doc_list in doc_lists:
            for d in doc_list:
                # Check if the document is already in the list
                if any(d.id == doc[0].id for doc in docs_with_rank):
                    continue
                # Calculate the rank using reciprocal rank fusion
                rank = self.reciprocal_rank_fusion(d, 10, doc_lists)
                docs_with_rank.append((d, rank))
        # Sort the documents based on rank
        docs_with_rank.sort(key=lambda x: x[1])
        return docs_with_rank[:topk]

    def rank_func(results, d):
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