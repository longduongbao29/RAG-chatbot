from langgraph.graph import StateGraph, START, END
from langchain_core.tools.base import BaseTool
from src.rag.pipeline.LangGraph.ToolsType import ToolManager
from src.database.DbManager import DbManager
from src.rag.strategy.query_translation.RagFusion import RAGFusion
from src.llm.Provider import LLMProvider
from src.llm.LLM import LLM
from src.llm.Schemas import LLMParams
from src.rag.pipeline.LangGraph.State import State
from src.rag.pipeline.LangGraph.Prompt import ANALYZE_TOOL_PROMPT,RAG_PROMPT,ANALYZE_QUERY_PROMPT, getPromptWithInstruction
from src.rag.pipeline.LangGraph.Schemas import AnalyzedTools,Decision

from src.utils.logger import setup_logger
from src.utils.helpers import format_history
from src.rag.pipeline.ChatPipeline import ChatPipeline
logger = setup_logger(__name__)

class Graph(ChatPipeline):

    def __init__(self, llm_params:LLMParams,
                 db_manager:DbManager,
                 tool_list:list,
                 prompt_instruction:str = None):
        self.llm_params = llm_params
        self.llm = LLMProvider(llm_params).provide_llm()
        self.query_translation = RAGFusion(self.llm)
       
        tool_manager = ToolManager(tool_list=tool_list,
                                   db_manager=db_manager,
                                   llm=self.llm)
        self.toolDescription= tool_manager.getToolDescription()
        self.tools:list[BaseTool] = tool_manager.getTools()
        self.prompt_instruction = prompt_instruction

        self.graph_builder = StateGraph(State)
        self.graph = self.build_graph()

    def analyze_query(self, state):
        logger.info("Analyzing query..")
        query = state["query"]
        history = state["history"]
        chain = ANALYZE_QUERY_PROMPT|self.llm.get_llm().with_structured_output(Decision)
        try:
            descision_invoke: Decision = chain.invoke({"input": query, "history": history})
            decision = descision_invoke.decision
        except Exception as e:
            logger.error(f"Error in analyzing query: {e}")
            state["decision"] = "answer"
        state["decision"] = decision
        return state

    def decision_router(self,state):
        logger.info("Decision: "+state["decision"])
        return state["decision"]

    def query_translation_node(self,state):
        logger.info("Query translation node")
        query = state['query']
        history = state['history']
        translated_queries = self.query_translation.translate(query, history)
        state["translated_queries"] = translated_queries
        return state

    def analyze_tool_node(self,state):
        logger.info("Analyzing tools...")
        input = f"Query: {state['query']}\nTranslated Queries: {state['translated_queries']}"
        chain = ANALYZE_TOOL_PROMPT| self.llm.get_llm().with_structured_output(AnalyzedTools)
        try:
            tools_name:AnalyzedTools = chain.invoke({"list_tools":self.toolDescription,
                                                     "input":input})
        except Exception as e:
            logger.error(f"Error in analyzing tools: {e}")
            tools_name = AnalyzedTools(tools=[])
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
        history = state["history"]
        if self.prompt_instruction:
            logger.info("Answer with instruction")
        prompt = getPromptWithInstruction(self.prompt_instruction) if self.prompt_instruction else RAG_PROMPT
        chain = prompt | self.llm.get_llm()
        try:
            answer = chain.invoke({
                "query":query,
                "context":context,
                "history":history
            })
            # logger.info(f"Context retrieved:{context}")
            content = LLM.remove_think_tags(answer.content)
        except Exception as e:
            logger.error(f"Error in chatbot node: {e}")
            content="Sorry, I'm having trouble processing your request. Please try again later."
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
        return self.graph_builder.compile()

    def run(self, record_chat:list):
        query = record_chat[-1]["message"]
        config = {"configurable": {"thread_id": "1"},"logging": {"level": "ERROR"} }
        events = self.graph.stream(
            {"query": query,
             "messages": [{"role": "user", "content": query}],
             "history": format_history(record_chat[:-1]),
             "translated_queries": [] ,
             "tools" : [],
             "context": "" },
            config,
            stream_mode="values",
        )
        answer = list(events)[-1]["messages"][-1]
        final_answer = LLM.postprocess(answer["content"])
        return final_answer
