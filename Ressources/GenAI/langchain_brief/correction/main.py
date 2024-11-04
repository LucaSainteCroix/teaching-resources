from fastapi import FastAPI
from routes import router
import os
from contextlib import asynccontextmanager
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv, find_dotenv
import logging

logger = logging.getLogger(__name__)

_ = load_dotenv(find_dotenv()) # read local .env file

azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY_4")
azure_openai_api_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT_4")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME_4")



# https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    try:
        logger.info("Starting up...")
        embeddings = AzureOpenAIEmbeddings(openai_api_key=azure_openai_api_key,
                                        azure_deployment='text-embedding-3-large',
                                        azure_endpoint=azure_openai_api_endpoint,
                                        openai_api_version="2023-05-15",
                                        chunk_size=500
        )
        app.state.vector_store = FAISS.load_local('faiss_vector_store', embeddings=embeddings, allow_dangerous_deserialization=True)
        yield
    except Exception as e:
        logger.error(f"An error occurred during startup: {e}")
        raise
    finally:
        logger.info("Shutting down...")


app = FastAPI(debug=True, lifespan=lifespan, logger=logger)

# Include the router from routes.py
app.include_router(router)
