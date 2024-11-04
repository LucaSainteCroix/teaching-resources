import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

from models import MainRequest

_ = load_dotenv(find_dotenv()) # read local .env file

azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY_4")
azure_openai_api_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT_4")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME_4")

llm = AzureChatOpenAI(api_key=azure_openai_api_key,
                        api_version="2023-12-01-preview",
                        azure_endpoint=azure_openai_api_endpoint,
                        model=deployment_name,
                        temperature=0
                        )


prompt = ChatPromptTemplate.from_messages([
    ("system", """You are helpful assistant here to decide which tool to use to answer questions about books.
     If the prompt is not about books, ignore it. If the tool needs a book_id, call it only if you are sure the user gave a book_id"""),
    ("user", "{input}"),
])


def decide_route(input_text, tools):

    llm_agent = llm.bind(functions=tools)

    chain = prompt | llm_agent | OpenAIFunctionsAgentOutputParser()

    result = chain.invoke(input_text)

    return result
