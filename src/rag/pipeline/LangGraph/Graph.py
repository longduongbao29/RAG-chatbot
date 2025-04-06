from injector import inject
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.rag.pipeline.LangGraph.ToolsType import Tools
from src.rag.strategy.query_translation.QueryTranslation import QueryTranslation
from src.rag.strategy.generation.Generation import LLMGenerator
from src.llm.LLM import LLM
from src.rag.pipeline.LangGraph.State import State
from src.rag.pipeline.LangGraph.Prompt import ANALYZE_TOOL_PROMPT,RAG_PROMPT,ANALYZE_QUERY_PROMPT
from src.rag.pipeline.LangGraph.Schemas import AnalyzedTools,Decision


from src.utils.logger import setup_logger
logger = setup_logger(__name__)

class Graph:
    @inject
    def __init__(self, 
                 llm:LLM, 
                 query_tranlation:QueryTranslation,
                 tools:Tools, 
                 generator:LLMGenerator):
        self.llm = llm.get_llm()
        self.tools = tools.tools
        self.query_translation = query_tranlation
        self.generator = generator
        self.graph_builder = StateGraph(State)
        self.memory = MemorySaver()
        self.graph = self.build_graph()

    def analyze_query(self, state):
        logger.info("Analyzing query..")
        query = state["query"]
        chain = ANALYZE_QUERY_PROMPT|self.llm.with_structured_output(Decision)
        decision: Decision = chain.invoke(query)
        state["decision"] = decision.decision
        return state
    
    def decision_router(self,state):
        logger.info("Decision: "+state["decision"])
        return state["decision"]
    
    def query_translation_node(self,state):
        logger.info("Query translation node")
        query = state['query']
        translated_queries = self.query_translation.translate(query)
        state["translated_queries"] = translated_queries
        return state
    
    def analyze_tool_node(self,state):
        logger.info("Analyzing tools...")
        input = f"Query: {state['query']}\nTranslated Queries: {state['translated_queries']}"
        chain = ANALYZE_TOOL_PROMPT| self.llm.with_structured_output(AnalyzedTools)
        tools_name:AnalyzedTools = chain.invoke(input)
        state["tools"] = [t for t in tools_name.tools]
        # logger.info("State\n", state)
        return state

    def retrieval_node(self, state):
        logger.info("Retrieval node")
        for tool_name in state["tools"]:
            for tool in self.tools:
                if tool_name ==  tool.name:
                    logger.info("Using tool "+ tool_name)
                    state["context"]+=tool.invoke(state)+"\n"
        return state
    def chatbot_node(self,state):
        logger.info("Chatbot node")
        query = state["query"]
        context = state["context"]
        chain = RAG_PROMPT|self.llm
        answer = chain.invoke({
            "query":query,
            "context":context
        })
        # logger.info(f"Context retrieved:{context}")
        content = LLM.remove_think_tags(answer.content)
        state["messages"].append({
            "role": "AI",
            "content": content
        })
        return state
    def build_graph(self):
        """
        Build the graph based on the query.
        """
        # Implement the logic to build the graph
        self.graph_builder.add_node("analyze_query",self.analyze_query)
        self.graph_builder.add_node("query_translation", self.query_translation_node)
        self.graph_builder.add_node("analyze_tool", self.analyze_tool_node)
        self.graph_builder.add_node("retrieve", self.retrieval_node)
        self.graph_builder.add_node("chatbot", self.chatbot_node)
        
        self.graph_builder.add_edge(START,"analyze_query")
        self.graph_builder.add_conditional_edges("analyze_query",self.decision_router,{
            "retrieve":"query_translation",
            "answer":"chatbot"
        })
        self.graph_builder.add_edge("query_translation","analyze_tool")
        self.graph_builder.add_edge("analyze_tool","retrieve")
        self.graph_builder.add_edge("retrieve","chatbot")
        self.graph_builder.add_edge("chatbot", END)
        return self.graph_builder.compile(checkpointer=self.memory)
        
    def run(self, query:str):
        
        config = {"configurable": {"thread_id": "1"},"logging": {"level": "ERROR"} }
        events = self.graph.stream(
            {"query": query,
             "messages": [{"role": "user", "content": query}],
             "translated_queries": [] ,
             "tools" : [],
             "context": "" },
            config,
            stream_mode="values",
        )
        
        return list(events)[-1]["messages"][-1]["content"]
               
        