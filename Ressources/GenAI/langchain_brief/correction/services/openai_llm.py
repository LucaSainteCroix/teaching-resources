import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate


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

question_answering_prompt_template = """
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know, but return the ebook id of the top document from the context if there is one.

Question: {question}

Context: {context}

Answer:
"""


prompt = ChatPromptTemplate.from_template(question_answering_prompt_template)

# Pour faire une string contenant tous les documents retournés par le retriever, séparés par 2 retours à la ligne
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

async def get_answer_with_rag(request, vector_store, output_schema):


    structured_llm = llm.with_structured_output(output_schema)

    retriever = vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.1, 'k': 4})

    # for debugging purposes
    # results = vector_store.similarity_search(query=request.question, k=4, search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.1})

    # for doc in results:
    #     print(f"* {doc.page_content} [{doc.metadata}]")

    qa_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(), # la question sera parsée comme le premier argument lors de l'invocation
        }
        | prompt
        | structured_llm
    )

    response = await qa_chain.ainvoke(request.question)

    return response
