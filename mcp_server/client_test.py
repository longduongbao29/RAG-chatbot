from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import asyncio

client = MultiServerMCPClient(
    {
        "elastic_server": {
             "url": "http://localhost:8001/mcp/",
            "transport": "streamable_http",
        },
        "milvus_server": {
            "url": "http://localhost:8002/mcp/",
            "transport": "streamable_http",
        }
    }
)

async def main():

    agent = create_react_agent(
        "openai:gpt-4.1-nano",
        tools= await client.get_tools(),
        prompt="You are a helpful assistant that can search products in an e-commerce database.",
    )

    # Example query to the agent
    messages = await agent.ainvoke(
        {"message": "Find me a smartphone under $500 from Samsung with good reviews."}
    )

    for message in messages["messages"]:
        if isinstance(message, AIMessage):
            print(f"AI: {message.content if message.content else message.additional_kwargs.get('tool_calls', [])}")
        elif isinstance(message, ToolMessage):
            print(f"Tool used: {message.content}")
        elif isinstance(message, HumanMessage):
            print(f"Human: {message.content}")
        else:
            print(f"Message: {message}")

if __name__ == "__main__":
    asyncio.run(main())