from src.dependency import injector
from src.rag.pipeline.LangGraph.Graph import Graph
instance = injector.get(Graph)
while True:
    print("AI: ",instance.run(input("User: ")))
