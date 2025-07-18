from os import getenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
PROMPT = ChatPromptTemplate([
    ("system", "You are a helpful AI bot."),
    ("human", "Curent conversation: {history}\nUser: {user_input}"),
])
llm = ChatOpenAI(api_key=getenv("OPENAI_API_KEY"),
                              model= "gpt-4o-mini",
                              temperature = 0.7)


chain = PROMPT | llm | StrOutputParser()
answer = chain.invoke({"user_input": "What is the strongest man in the world?", "history": ""})
print(answer)