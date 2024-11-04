import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.docstore.in_memory import InMemoryDocstore


from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY_4")
azure_openai_api_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT_4")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME_4")

embeddings = AzureOpenAIEmbeddings(openai_api_key=azure_openai_api_key,
                                    azure_deployment='text-embedding-3-large',
                                    azure_endpoint=azure_openai_api_endpoint,
                                    openai_api_version="2023-05-15",
                                    chunk_size=500
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# def get_documents_from_rag(question):

#     retriever = vectorstore.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.1})

#     docs = retriever.invoke(question)
#     docs_string = format_docs(docs)
#     return docs_string


async def create_vector_store_from_full_text(full_text, book_id):

    try:
        vector_store = FAISS.load_local('cached_vector_stores',
                                        embeddings=embeddings,
                                        index_name=str(book_id),
                                        allow_dangerous_deserialization=True)
        return vector_store
    except Exception as e:
        print(e)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)

    split_text = text_splitter.split_text(full_text)

    # docs = text_splitter.create_documents(split_text)

    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore= InMemoryDocstore(),
        index_to_docstore_id={}
    )
    await vector_store.aadd_texts(split_text)

    vector_store.save_local('cached_vector_stores', index_name=str(book_id))
# vector_store = FAISS.from_documents(docs, embedding=embeddings)

    return vector_store
